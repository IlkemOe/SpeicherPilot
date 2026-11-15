"""SpeicherPilot – Speicherplatz verstehen und freiräumen.

Startet einen lokalen Server (nur 127.0.0.1) und öffnet die Oberfläche als App-Fenster in Edge.
"""
import json
import logging
import os
import secrets
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

import cleanup  # noqa: E402
import games  # noqa: E402
import knowledge  # noqa: E402
import scanner  # noqa: E402
import winapi  # noqa: E402

VERSION = "1.0"
PREFERRED_PORT = 8765
UI_DIR = os.path.join(APP_DIR, "ui")
DATA_DIR = os.path.join(knowledge.LOCAL, "SpeicherPilot")
os.makedirs(DATA_DIR, exist_ok=True)

logging.basicConfig(filename=os.path.join(DATA_DIR, "log.txt"), level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
log = logging.getLogger("speicherpilot")

if sys.stdout is None:  # pythonw
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.path.join(DATA_DIR, "stderr.txt"), "a", encoding="utf-8")

TOKEN = secrets.token_urlsafe(24)
SCANNER = scanner.Scanner(skip_paths=[knowledge.WINDIR, os.path.join(DATA_DIR)])
JUNK = cleanup.Junk()


def _game_size(path):
    node = SCANNER.get(path)
    if node is not None:
        return node.size, node.mtime, node.files
    fl, _, _ = cleanup._walk_files(path)
    return sum(f[1] for f in fl), max((f[2] for f in fl), default=0), len(fl)


GAMES = games.Games(_game_size)
knowledge.GAME_HOOK = GAMES.lookup
SCANNER.on_done = GAMES.refresh_sync


class Life:
    last_beat = time.time()
    deadline = None
    busy = 0
    session_freed = 0
    server = None


# ------------------------------------------------------------------ API-Funktionen
def _age_days(t):
    return max(0, (time.time() - t) / 86400) if t else 99999


def api_info(_q):
    return {"version": VERSION, "admin": winapi.is_admin(), "user": os.environ.get("USERNAME", ""),
            "home": knowledge.HOME, "knownFolders": knowledge.KF, "sessionFreed": Life.session_freed,
            "levels": knowledge.LEVELS}


def api_drives(_q):
    return {"drives": winapi.drives(), "recycleBin": winapi.recycle_bin_info()}


def api_status(_q):
    return SCANNER.status()


def _node_json(n, with_info=False):
    d = {"path": n.path, "name": n.name, "size": n.size, "files": n.files, "dirs": n.dirs,
         "mtime": n.mtime, "atime": n.atime, "kind": n.kind, "denied": n.denied,
         "hasChildren": bool(n.children)}
    if with_info and n.kind == "dir":
        age = _age_days(n.mtime)
        d["info"] = knowledge.classify_folder(n.path, age, n.size)
    return d


def _grandkids(c, limit=30):
    if c.kind == "system":
        return []
    ks = sorted(c.children, key=lambda k: k.size, reverse=True)
    out = [{"path": None if k.kind == "system" else k.path, "name": k.name, "size": k.size,
            "mtime": k.mtime, "kind": k.kind} for k in ks[:limit] if k.size > 0]
    rest = sum(k.size for k in ks[limit:])
    if rest > 0:
        out.append({"path": None, "name": f"{len(ks) - limit} weitere", "size": rest, "kind": "other",
                    "mtime": max((k.mtime for k in ks[limit:]), default=0)})
    if c.own > 0 and c.kind != "virtual":
        out.append({"path": None, "name": "Dateien", "size": c.own, "kind": "files", "mtime": c.mtime})
    return out


_SUMMARY_CACHE = {}


def _content_summary(path, budget=1.2, max_files=40000):
    if path in _SUMMARY_CACHE:
        return _SUMMARY_CACHE[path]
    t0 = time.time()
    sizes, total, n = {}, 0, 0
    stack = [path]
    complete = True
    while stack:
        if n > max_files or time.time() - t0 > budget:
            complete = False
            break
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if st.st_file_attributes & 0x10:
                        if not st.st_file_attributes & 0x400:
                            stack.append(e.path)
                        continue
                    if st.st_file_attributes & scanner.ATTR_CLOUD:
                        continue
                    g = knowledge.ext_group(os.path.splitext(e.name)[1].lower())
                    sizes[g] = sizes.get(g, 0) + st.st_size
                    total += st.st_size
                    n += 1
        except OSError:
            continue
    if not total:
        res = None
    else:
        res = [{"label": g, "pct": round(v * 100 / total)}
               for g, v in sorted(sizes.items(), key=lambda kv: -kv[1])[:3] if v * 100 / total >= 5]
    _SUMMARY_CACHE[path] = res
    return res


def api_tree(q):
    path = q.get("path", [""])[0]
    with SCANNER.lock:
        node = SCANNER.get(path)
        if node is None:
            return {"error": "Ordner nicht im Analyse-Ergebnis."}
        kids = sorted(node.children, key=lambda c: c.size, reverse=True)
        children = []
        for c in kids[:90]:
            if c.size <= 0:
                continue
            d = _node_json(c)
            d["kids"] = _grandkids(c)
            children.append(d)
        rest = kids[90:]
        if rest:
            rs = sum(c.size for c in rest)
            if rs > 0:
                children.append({"path": None, "name": f"{len(rest)} weitere Ordner", "size": rs, "kind": "other",
                                 "mtime": max((c.mtime for c in rest), default=0),
                                 "atime": max((c.atime for c in rest), default=0), "hasChildren": False})
        if node.own > 0 and node.kind != "virtual":
            children.append({"path": None, "name": "Dateien direkt in diesem Ordner", "size": node.own,
                             "kind": "files", "mtime": node.mtime, "atime": node.atime, "hasChildren": False})
        crumbs = []
        x = node
        while x is not None:
            crumbs.append({"path": x.path, "name": x.name})
            x = x.parent
        return {"node": _node_json(node, True), "children": children, "crumbs": list(reversed(crumbs))}


def api_unused(q):
    days = float(q.get("days", ["180"])[0])
    minsize = int(float(q.get("min", ["100"])[0]) * 1024 * 1024)
    basis = q.get("basis", ["modified"])[0]
    rows = []
    for n, age in SCANNER.unused(days, minsize, basis):
        info = knowledge.classify_folder(n.path, age, n.size)
        rows.append({"path": n.path, "name": n.name, "size": n.size, "files": n.files, "mtime": n.mtime,
                     "atime": n.atime, "age": round(age, 1), "info": info,
                     "score": knowledge.score(info["level"], age, n.size)})
    rows.sort(key=lambda r: (r["score"], r["size"]), reverse=True)
    rows = rows[:400]
    deadline = time.time() + 8
    for r in sorted(rows, key=lambda r: -r["size"]):
        if r["path"] in _SUMMARY_CACHE or time.time() < deadline:
            r["contents"] = _content_summary(r["path"])
    return {"items": rows, "total": len(rows)}


def api_large(q):
    minsize = int(float(q.get("min", ["500"])[0]) * 1024 * 1024)
    rows = []
    with SCANNER.lock:
        files = list(SCANNER.large)
    for f in files:
        if f["size"] < minsize:
            continue
        age = _age_days(f["mtime"])  # Zugriffszeit ist unter Windows unzuverlässig (Scanner, Indexer)
        info = knowledge.classify_file(f["path"], age, f["size"])
        rows.append({"path": f["path"], "name": os.path.basename(f["path"]), "size": f["size"],
                     "mtime": f["mtime"], "atime": f["atime"], "age": round(age, 1), "info": info,
                     "ext": os.path.splitext(f["path"])[1].lower(),
                     "score": knowledge.score(info["level"], age, f["size"])})
    return {"items": rows}


def api_junk(_q):
    return JUNK.snapshot()


def api_games(_q):
    return GAMES.snapshot()


def post_games_refresh(_b):
    GAMES.refresh_async()
    return {"ok": True}


def api_recyclebin(_q):
    return winapi.recycle_bin_info()


# ------------------------------------------------------------------ POST
def post_scan(body):
    _SUMMARY_CACHE.clear()
    ok, err = SCANNER.start(body.get("roots") or [])
    return {"ok": ok, "error": err}


def post_scan_cancel(_b):
    SCANNER.cancel()
    return {"ok": True}


def post_junk_measure(_b):
    threading.Thread(target=JUNK.measure_all, daemon=True).start()
    return {"ok": True}


def api_junk_items(q):
    items, total = JUNK.items(q.get("id", [""])[0])
    return {"items": items, "total": total}


def api_folder_items(q):
    path = q.get("path", [""])[0]
    if not path or not (SCANNER.in_scope(path) or GAMES.is_leftover(path)) or not os.path.isdir(path):
        return {"error": "Ordner nicht verfügbar"}
    out = []
    try:
        entries = list(os.scandir(path))
    except OSError as exc:
        return {"error": str(exc)}
    for e in entries:
        try:
            st = e.stat(follow_symlinks=False)
        except OSError:
            continue
        is_dir = bool(st.st_file_attributes & 0x10)
        if is_dir:
            node = SCANNER.get(e.path)
            if node is not None:
                size, mtime, count = node.size, node.mtime, node.files
            else:
                fl, _, _ = cleanup._walk_files(e.path)
                size, count = sum(f[1] for f in fl), len(fl)
                mtime = max((f[2] for f in fl), default=st.st_mtime)
            kind = None  # wird unten für die größten Ordner ergänzt
        else:
            size = 0 if st.st_file_attributes & scanner.ATTR_CLOUD else st.st_size
            mtime, count = st.st_mtime, 1
            kind = knowledge.ext_group(os.path.splitext(e.name)[1].lower())
        out.append({"path": e.path, "name": e.name, "sub": kind, "size": size, "mtime": mtime,
                    "isDir": is_dir, "count": count})
    out.sort(key=lambda x: -x["size"])
    deadline = time.time() + 3
    for it in out:
        if it["sub"] is None:
            summ = _content_summary(it["path"], budget=0.4) if time.time() < deadline else None
            it["sub"] = "Ordner" + (f" · vor allem {summ[0]['label']}" if summ else "")
    return {"items": out[:3000], "total": len(out)}


def post_recycle_restore(body):
    results = []
    for p in [p for p in body.get("paths", []) if isinstance(p, str)][:500]:
        ok, msg = winapi.recycle_bin_restore(p)
        results.append({"path": p, "ok": ok, "error": None if ok else msg, "restored": msg if ok else None})
        log.info("Wiederhergestellt %s -> %s (%s)", p, msg, ok)
    threading.Thread(target=JUNK.measure_all, daemon=True).start()
    return {"results": results, "recycleBin": winapi.recycle_bin_info()}


def post_junk_clean(body):
    ids = [i for i in body.get("ids", []) if isinstance(i, str)]
    exclude = body.get("exclude") if isinstance(body.get("exclude"), dict) else {}
    Life.busy += 1
    try:
        res = JUNK.clean(ids, exclude)
    finally:
        Life.busy -= 1
    freed = sum(r["freed"] for r in res)
    Life.session_freed += freed
    log.info("Schnellreinigung %s: %d Bytes", ids, freed)
    return {"results": res, "freed": freed, "sessionFreed": Life.session_freed, "junk": JUNK.snapshot()}


def _measure(path):
    if os.path.isfile(path):
        try:
            return os.stat(path).st_size
        except OSError:
            return 0
    total = 0
    files, _, _ = cleanup._walk_files(path)
    for _, sz, _ in files:
        total += sz
    return total


def _rmtree(path):
    def onexc(func, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path, onexc=onexc)
    else:
        try:
            os.remove(path)
        except PermissionError:
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)


def _delete_check(path):
    if not path or not os.path.isabs(path):
        return "Ungültiger Pfad"
    if not os.path.exists(path):
        return "Existiert nicht mehr"
    if not SCANNER.in_scope(path) and not GAMES.is_leftover(path):
        return "Liegt nicht im analysierten Bereich"
    p = knowledge.nc(path)
    if knowledge.is_container(path):
        return "Sammelordner werden nicht als Ganzes gelöscht"
    if os.path.isdir(path):
        info = knowledge.classify_folder(path)
    else:
        info = knowledge.classify_file(path)
    if info.get("protect"):
        return info["protect"]
    for base in [knowledge.WINDIR, knowledge.PROGRAMDATA, *knowledge.PROGRAM_FILES, knowledge.APP_DIR, DATA_DIR]:
        if knowledge.under(p, base):
            return "Geschützter Bereich"
    return None


def _delete_except(path, keep, mode):
    """Inhalt eines Ordners löschen, ausgewählte Einträge (direkte Kinder) aber behalten."""
    try:
        children = [e.path for e in os.scandir(path)]
    except OSError as exc:
        return {"path": path, "ok": False, "error": str(exc), "freed": 0}
    targets = [c for c in children if knowledge.nc(c) not in keep]
    sizes = {c: _measure(c) for c in targets}
    try:
        if mode == "recycle":
            winapi.move_to_recycle_bin(targets)
        else:
            for c in targets:
                try:
                    _rmtree(c)
                except OSError:
                    pass
    except Exception as exc:
        log.warning("Löschen fehlgeschlagen %s: %s", path, exc)
    freed = 0
    failed = 0
    for c in targets:
        gone = not os.path.exists(c)
        f = sizes[c] if gone else max(0, sizes[c] - _measure(c))
        freed += f
        failed += 0 if gone else 1
        SCANNER.remove_path(c, f, gone)
    _SUMMARY_CACHE.pop(path, None)
    log.info("Gelöscht (%s) Inhalt von %s außer %d behaltenen: %d Bytes", mode, path, len(keep), freed)
    entry = {"path": path, "ok": failed == 0, "freed": freed, "kept": len(keep), "partial": failed > 0 and freed > 0}
    if failed:
        entry["error"] = f"{failed} Einträge konnten nicht gelöscht werden (in Benutzung oder keine Rechte)."
    return entry


def post_delete(body):
    mode = "permanent" if body.get("mode") == "permanent" else "recycle"
    paths = [p for p in body.get("paths", []) if isinstance(p, str)][:500]
    keep_map = body.get("keep") if isinstance(body.get("keep"), dict) else {}
    results = []
    total = 0
    Life.busy += 1
    try:
        for path in paths:
            err = _delete_check(path)
            if err:
                results.append({"path": path, "ok": False, "error": err, "freed": 0})
                continue
            keep = {knowledge.nc(k) for k in keep_map.get(path, []) if isinstance(k, str)}
            if keep and os.path.isdir(path):
                entry = _delete_except(path, keep, mode)
                total += entry["freed"]
                results.append(entry)
                continue
            size = _measure(path)
            try:
                if mode == "recycle":
                    ok = winapi.move_to_recycle_bin(path)
                    if not ok and os.path.exists(path):
                        raise OSError("Windows konnte das Element nicht in den Papierkorb verschieben "
                                      "(evtl. geöffnet oder Pfad zu lang).")
                else:
                    _rmtree(path)
            except Exception as exc:
                log.warning("Löschen fehlgeschlagen %s: %s", path, exc)
            gone = not os.path.exists(path)
            remaining = 0 if gone else _measure(path)
            freed = max(0, size - remaining)
            total += freed
            SCANNER.remove_path(path, freed, gone)
            if gone:
                GAMES.remove(path)
            _SUMMARY_CACHE.pop(path, None)
            entry = {"path": path, "ok": gone, "freed": freed, "partial": (not gone and freed > 0)}
            if not gone:
                entry["error"] = ("Teilweise gelöscht – einige Dateien sind gerade in Benutzung."
                                  if freed > 0 else "Konnte nicht gelöscht werden (in Benutzung oder keine Rechte).")
            results.append(entry)
            log.info("Gelöscht (%s) %s: %d Bytes, vollständig=%s", mode, path, freed, gone)
    finally:
        Life.busy -= 1
    Life.session_freed += total
    return {"results": results, "freed": total, "mode": mode, "sessionFreed": Life.session_freed,
            "recycleBin": winapi.recycle_bin_info()}


def post_recycle_empty(_b):
    before = winapi.recycle_bin_info()["size"]
    winapi.empty_recycle_bin()
    info = winapi.recycle_bin_info()
    return {"ok": True, "freed": max(0, before - info["size"]), "recycleBin": info}


def post_open(body):
    path = body.get("path") or ""
    if not os.path.exists(path):
        return {"ok": False, "error": "Pfad existiert nicht"}
    if os.path.isdir(path):
        subprocess.Popen(["explorer", os.path.normpath(path)])
    else:
        subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')
    return {"ok": True}


_SETTINGS = {"apps": "ms-settings:appsfeatures", "storage": "ms-settings:storagesense",
             "steam": "steam://open/games"}


def post_action(body):
    target = body.get("target")
    if target == "onedrive":
        return post_open({"path": body.get("path")})
    if target == "steam-uninstall":
        appid = str(body.get("appid") or "")
        if not appid.isdigit():
            return {"ok": False, "error": "Ungültige App-ID"}
        uri = f"steam://uninstall/{appid}"
    else:
        uri = _SETTINGS.get(target)
    if not uri:
        return {"ok": False}
    try:
        os.startfile(uri)
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True}


def post_pick_folder(_b):
    code = ("import tkinter as tk, tkinter.filedialog as fd; r=tk.Tk(); r.withdraw(); "
            "r.attributes('-topmost', True); p=fd.askdirectory(title='Ordner für die Analyse wählen'); "
            "print(p or '', end='')")
    exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(exe):
        exe = sys.executable
    try:
        out = subprocess.run([exe, "-c", code], capture_output=True, text=True, timeout=600,
                             encoding="utf-8").stdout.strip()
    except Exception as exc:
        return {"path": None, "error": str(exc)}
    return {"path": os.path.normpath(out) if out else None}


def post_heartbeat(_b):
    Life.last_beat = time.time()
    Life.deadline = None
    return {"ok": True}


def post_bye(_b):
    Life.deadline = time.time() + 8
    return {"ok": True}


def post_elevate(_b):
    ok = winapi.relaunch_as_admin(os.path.abspath(__file__), "--elevated")
    if ok:
        threading.Timer(1.0, shutdown).start()
    return {"ok": ok}


GET_ROUTES = {"/api/info": api_info, "/api/drives": api_drives, "/api/status": api_status,
              "/api/tree": api_tree, "/api/unused": api_unused, "/api/large": api_large,
              "/api/junk": api_junk, "/api/recyclebin": api_recyclebin,
              "/api/junk/items": api_junk_items, "/api/folder/items": api_folder_items, "/api/games": api_games}
POST_ROUTES = {"/api/scan": post_scan, "/api/scan/cancel": post_scan_cancel,
               "/api/junk/measure": post_junk_measure, "/api/junk/clean": post_junk_clean,
               "/api/delete": post_delete, "/api/recyclebin/empty": post_recycle_empty,
               "/api/recyclebin/restore": post_recycle_restore, "/api/games/refresh": post_games_refresh,
               "/api/open": post_open, "/api/action": post_action, "/api/pick-folder": post_pick_folder,
               "/api/heartbeat": post_heartbeat, "/api/bye": post_bye, "/api/elevate": post_elevate}

MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
        ".ico": "image/x-icon"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "SpeicherPilot"

    def log_message(self, fmt, *args):
        pass

    def _allowed_host(self):
        port = self.server.server_address[1]
        return self.headers.get("Host", "") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _token_ok(self, query):
        t = self.headers.get("X-Token") or query.get("t", [""])[0]
        return secrets.compare_digest(t, TOKEN)

    def do_GET(self):
        if not self._allowed_host():
            return self._send(403, b"Forbidden", "text/plain")
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            with open(os.path.join(UI_DIR, "index.html"), encoding="utf-8") as f:
                html = f.read().replace("__TOKEN__", TOKEN)
            return self._send(200, html.encode("utf-8"), MIME[".html"])
        if u.path.startswith("/static/"):
            name = os.path.basename(u.path)
            fp = os.path.join(UI_DIR, name)
            ext = os.path.splitext(name)[1]
            if ext in MIME and os.path.isfile(fp):
                with open(fp, "rb") as f:
                    return self._send(200, f.read(), MIME[ext])
            return self._send(404, b"Not found", "text/plain")
        if u.path == "/api/ping":
            return self._json({"app": "SpeicherPilot"})
        fn = GET_ROUTES.get(u.path)
        if not fn:
            return self._send(404, b"Not found", "text/plain")
        if not self._token_ok(q):
            return self._json({"error": "Nicht autorisiert"}, 403)
        try:
            self._json(fn(q))
        except Exception as exc:
            log.exception("GET %s", u.path)
            self._json({"error": str(exc)}, 500)

    def do_POST(self):
        if not self._allowed_host():
            return self._send(403, b"Forbidden", "text/plain")
        origin = self.headers.get("Origin")
        port = self.server.server_address[1]
        if origin and origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"):
            return self._send(403, b"Forbidden", "text/plain")
        u = urlparse(self.path)
        q = parse_qs(u.query)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        fn = POST_ROUTES.get(u.path)
        if not fn:
            return self._send(404, b"Not found", "text/plain")
        if not self._token_ok(q):
            return self._json({"error": "Nicht autorisiert"}, 403)
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(body, dict):
                body = {}
        except ValueError:
            body = {}
        try:
            self._json(fn(body))
        except Exception as exc:
            log.exception("POST %s", u.path)
            self._json({"error": str(exc)}, 500)


# ------------------------------------------------------------------ Start / Fenster
def find_edge():
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), knowledge.LOCAL):
        if base:
            p = os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe")
            if os.path.exists(p):
                return p
    return None


def open_window(url):
    edge = find_edge()
    if edge:
        profile = os.path.join(DATA_DIR, "edge-profile")
        try:
            subprocess.Popen([edge, f"--app={url}", "--window-size=1440,920", f"--user-data-dir={profile}",
                              "--no-first-run", "--no-default-browser-check", "--disable-sync",
                              "--disable-features=Translate"])
            return
        except OSError:
            pass
    import webbrowser
    webbrowser.open(url)


def existing_instance(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ping", timeout=1.5) as r:
            return json.loads(r.read()).get("app") == "SpeicherPilot"
    except Exception:
        return False


def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def shutdown():
    log.info("Beende SpeicherPilot")
    if Life.server:
        threading.Thread(target=Life.server.shutdown, daemon=True).start()


def watchdog():
    while True:
        time.sleep(2)
        now = time.time()
        if Life.busy or SCANNER.state == "scanning":
            continue
        if Life.deadline and now > Life.deadline:
            return shutdown()
        if now - Life.last_beat > 180:
            return shutdown()


def main():
    elevated = "--elevated" in sys.argv
    no_window = "--no-window" in sys.argv
    port = PREFERRED_PORT
    if elevated:
        for _ in range(25):
            if port_free(port):
                break
            time.sleep(0.2)
    if not port_free(port):
        if existing_instance(port) and not elevated:
            open_window(f"http://127.0.0.1:{port}/")
            return
        port = 0
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    Life.server = server
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    log.info("SpeicherPilot %s läuft auf %s (Admin: %s)", VERSION, url, winapi.is_admin())
    print(f"SpeicherPilot läuft auf {url}", flush=True)
    threading.Thread(target=JUNK.measure_all, daemon=True).start()
    threading.Thread(target=knowledge.installed_tokens, daemon=True).start()
    GAMES.refresh_async()
    threading.Thread(target=watchdog, daemon=True).start()
    if not no_window:
        open_window(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
