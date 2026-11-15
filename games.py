"""Spiele erkennen: installierte Spiele (Steam, GOG, Epic, Ubisoft, Rockstar, Xbox, …),
dazugehörige Daten (Spielstände, Einstellungen, Caches) und Überreste deinstallierter Spiele."""
import glob
import json
import os
import re
import threading
import time
import winreg

import knowledge
from knowledge import HOME, KF, LOCAL, LOCALLOW, nc, under

HKLM, HKCU = winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER

# Ordnernamen von Entwicklern/Publishern, deren Unterordner einzelne Spiele sind
KNOWN_DEVS = {
    "cd projekt red", "rockstar games", "larian studios", "ubisoft", "bethesda softworks", "paradox interactive",
    "electronic arts", "fromsoftware", "activision", "blizzard entertainment", "2k", "2k games", "bandai namco",
    "capcom", "sega", "square enix", "warhorse studios", "hello games", "frontier developments", "remedy",
    "embark", "ncsoft", "eidos montreal", "io interactive", "techland", "id software", "avalanche studios",
    "supermassive games", "kojima productions", "re-logic", "klei", "mojang studios", "gearbox", "kunos simulazioni",
    "codemasters", "obsidian entertainment", "my games",
}
SYSTEM_DEVS = {"microsoft", "amd", "intel", "nvidia", "nvidia corporation", "temp", "unity", "google", "mozilla",
               "apple", "adobe", "sun", "oracle", "packages", "defaultcompany", "unity technologies"}
# Entwickler, deren Ordner in AppData\Local zuverlässig je Spiel einen Unterordner haben
RELIABLE_DEVS = {"cd projekt red", "larian studios", "warhorse studios", "remedy", "techland", "avalanche studios",
                 "frontier developments", "paradox interactive", "fromsoftware", "bethesda softworks",
                 "io interactive", "hello games", "re-logic", "klei", "eidos montreal", "supermassive games",
                 "kojima productions", "codemasters", "obsidian entertainment"}
NOT_A_GAME = re.compile(r"launcher|client|social ?club|beacon|installer|crashreport|redistributable|"
                        r"ubisoft connect|^ea app|^origin$|battle\.net|galaxy|"
                        r"vanguard|anticheat|anti-cheat|easyanticheat|battleye|update|^cache$|^logs?$|webcache|"
                        r"overlay|^config$|desktop\.ini|^unrealengine|^engine$|^common$", re.I)
GAME_PUBLISHERS = re.compile(r"riot games|electronic arts|blizzard|bethesda|activision|mojang|rockstar|"
                             r"cd projekt|ubisoft|bandai|capcom|square enix|sega|2k|warner bros\. games|"
                             r"focus entertainment|paradox|devolver|team17|thq nordic|deep silver|krafton", re.I)
STEAM_SKIP_APPS = {"228980"}  # Steamworks Common Redistributables
STEAM_SKIP_DIRS = {"steamworks shared", "steam controller configs", "steamvr"}


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _subkeys(hive, key):
    out = []
    try:
        with winreg.OpenKey(hive, key) as k:
            i = 0
            while True:
                try:
                    out.append(winreg.EnumKey(k, i))
                except OSError:
                    break
                i += 1
    except OSError:
        pass
    return out


def _values(hive, key):
    out = {}
    try:
        with winreg.OpenKey(hive, key) as k:
            i = 0
            while True:
                try:
                    n, v, _ = winreg.EnumValue(k, i)
                except OSError:
                    break
                out[n] = v
                i += 1
    except OSError:
        pass
    return out


def _acf(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return {}
    return {k: v for k, v in re.findall(r'^\t"(\w+)"\t\t"([^"]*)"', text, re.M)}


def _isdir(p):
    try:
        return bool(p) and os.path.isdir(p)
    except OSError:
        return False


def _subdirs(p):
    try:
        return [e for e in os.scandir(p) if e.is_dir(follow_symlinks=False)]
    except OSError:
        return []


# ------------------------------------------------------------------ installierte Spiele
def _steam():
    installed, leftovers, libs = [], [], []
    sp = _values(HKCU, r"Software\Valve\Steam").get("SteamPath") or \
        _values(HKLM, r"SOFTWARE\WOW6432Node\Valve\Steam").get("InstallPath")
    if not sp:
        return installed, leftovers
    sp = os.path.normpath(sp)
    libs.append(sp)
    try:
        vdf = open(os.path.join(sp, "steamapps", "libraryfolders.vdf"), encoding="utf-8", errors="replace").read()
        for p in re.findall(r'"path"\s+"([^"]+)"', vdf):
            p = os.path.normpath(p.replace("\\\\", "\\"))
            if nc(p) not in {nc(x) for x in libs}:
                libs.append(p)
    except OSError:
        pass
    ids = set()
    for lib in libs:
        sa = os.path.join(lib, "steamapps")
        known = set()
        for m in glob.glob(os.path.join(sa, "appmanifest_*.acf")):
            d = _acf(m)
            appid, idir = d.get("appid"), d.get("installdir")
            if not appid or not idir:
                continue
            path = os.path.join(sa, "common", idir)
            known.add(nc(path))
            ids.add(appid)
            if appid in STEAM_SKIP_APPS or not _isdir(path):
                continue
            installed.append({"id": f"steam:{appid}", "appid": appid, "name": d.get("name") or idir,
                              "launcher": "Steam", "path": path, "size": int(d.get("SizeOnDisk") or 0),
                              "lastPlayed": int(d.get("LastPlayed") or 0), "aliases": [idir]})
        for e in _subdirs(os.path.join(sa, "common")):
            if nc(e.path) not in known and e.name.lower() not in STEAM_SKIP_DIRS:
                leftovers.append({"path": e.path, "name": e.name, "kind": "install", "launcher": "Steam"})
        for sub, kind in (("shadercache", "shader"), (os.path.join("workshop", "content"), "workshop")):
            for e in _subdirs(os.path.join(sa, sub)):
                if e.name.isdigit() and e.name not in ids:
                    leftovers.append({"path": e.path, "name": f"Steam-App {e.name}", "kind": kind,
                                      "launcher": "Steam", "appid": e.name})
    return installed, leftovers


def _gog():
    out = []
    for sub in _subkeys(HKLM, r"SOFTWARE\WOW6432Node\GOG.com\Games"):
        v = _values(HKLM, rf"SOFTWARE\WOW6432Node\GOG.com\Games\{sub}")
        if _isdir(v.get("path")):
            out.append({"id": f"gog:{sub}", "name": v.get("gameName") or os.path.basename(v["path"]),
                        "launcher": "GOG", "path": os.path.normpath(v["path"])})
    return out


def _epic():
    out = []
    for f in glob.glob(os.path.join(knowledge.PROGRAMDATA, "Epic", "EpicGamesLauncher", "Data", "Manifests", "*.item")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if _isdir(d.get("InstallLocation")):
            out.append({"id": f"epic:{d.get('AppName')}", "name": d.get("DisplayName") or d.get("AppName"),
                        "launcher": "Epic Games", "path": os.path.normpath(d["InstallLocation"]),
                        "size": int(d.get("InstallSize") or 0)})
    return out


def _ubisoft():
    out = []
    for sub in _subkeys(HKLM, r"SOFTWARE\WOW6432Node\Ubisoft\Launcher\Installs"):
        p = _values(HKLM, rf"SOFTWARE\WOW6432Node\Ubisoft\Launcher\Installs\{sub}").get("InstallDir")
        if _isdir(p):
            p = os.path.normpath(p)
            name = _values(HKLM, rf"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Uplay Install {sub}").get("DisplayName")
            pretty = re.sub(r"(?<=[a-z])(?=[A-Z0-9])", " ", os.path.basename(p))
            out.append({"id": f"ubi:{sub}", "name": name or pretty, "launcher": "Ubisoft Connect", "path": p,
                        "aliases": [os.path.basename(p)]})
    return out


def _rockstar():
    out = []
    for sub in _subkeys(HKLM, r"SOFTWARE\WOW6432Node\Rockstar Games"):
        if NOT_A_GAME.search(sub):
            continue
        p = _values(HKLM, rf"SOFTWARE\WOW6432Node\Rockstar Games\{sub}").get("InstallFolder")
        if _isdir(p):
            p = os.path.normpath(p)
            name = sub.replace("GTAV", "GTA V")
            out.append({"id": f"rockstar:{sub}", "name": name, "launcher": "Rockstar Games", "path": p,
                        "aliases": [sub, "GTA V" if "GTAV" in sub else sub]})
    return out


def _uninstall_registry():
    out = []
    for hive, key in ((HKLM, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                      (HKLM, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                      (HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")):
        for sub in _subkeys(hive, key):
            if sub.startswith("Steam App") or sub.startswith("Uplay Install"):
                continue
            v = _values(hive, rf"{key}\{sub}")
            name, pub, loc = v.get("DisplayName"), v.get("Publisher") or "", v.get("InstallLocation")
            if not name or not GAME_PUBLISHERS.search(pub) or NOT_A_GAME.search(name):
                continue
            if not _isdir(loc):
                continue
            launcher = "Riot Client" if "riot" in pub.lower() else "EA app" if "electronic arts" in pub.lower() \
                else "Battle.net" if "blizzard" in pub.lower() else pub.split(",")[0]
            out.append({"id": f"reg:{sub}", "name": name, "launcher": launcher, "path": os.path.normpath(loc)})
    return out


def _xbox():
    out = []
    for d in knowledge.winapi.drives():
        for e in _subdirs(os.path.join(d["root"], "XboxGames")):
            out.append({"id": f"xbox:{e.name}", "name": e.name, "launcher": "Xbox", "path": e.path})
    return out


def _aliases(game):
    al = {_norm(game["name"]), _norm(os.path.basename(game["path"]))}
    al.update(_norm(a) for a in game.get("aliases", []))
    for e in _subdirs(game["path"])[:40]:
        n = e.name
        if n.lower().endswith("_data"):
            al.add(_norm(n[:-5]))
        elif _isdir(os.path.join(e.path, "Binaries")) or _isdir(os.path.join(e.path, "Content", "Paks")):
            al.add(_norm(n))
    return {a for a in al if len(a) >= 3}


def _matches(aliases, name):
    c = _norm(name)
    if len(c) < 3:
        return False
    for a in aliases:
        if a == c:
            return True
        short, long_ = sorted((a, c), key=len)
        if len(short) >= 6 and short in long_:
            return True
        if long_.startswith(short) and len(short) >= max(3, len(long_) * 0.3):
            return True
    return False


# ------------------------------------------------------------------ Spieldaten außerhalb der Installation
def _data_candidates():
    """(Pfad, Art, sicher_ein_Spiel) – Orte, an denen Spiele Spielstände/Einstellungen/Caches ablegen."""
    out = []
    docs, saved = KF.get("documents", ""), KF.get("savedgames", "")

    def add_dev_children(dev_path, label, sure=True):
        for g in _subdirs(dev_path):
            if not NOT_A_GAME.search(g.name):
                out.append((g.path, label, sure))

    for e in _subdirs(os.path.join(docs, "My Games")):
        if not NOT_A_GAME.search(e.name):
            out.append((e.path, "Spielstände & Einstellungen", True))
    for e in _subdirs(saved):
        if e.name.lower() in KNOWN_DEVS:
            add_dev_children(e.path, "Spielstände")
        elif not NOT_A_GAME.search(e.name):
            out.append((e.path, "Spielstände", True))
    for e in _subdirs(LOCALLOW):
        if e.name.lower() in SYSTEM_DEVS or NOT_A_GAME.search(e.name):
            continue
        kids = [g for g in _subdirs(e.path) if not NOT_A_GAME.search(g.name)]
        if kids:
            for g in kids:
                out.append((g.path, "Spielstände & Einstellungen", True))
        else:
            out.append((e.path, "Spielstände & Einstellungen", True))
    for e in _subdirs(LOCAL):
        low = e.name.lower()
        if low in KNOWN_DEVS:
            add_dev_children(e.path, "Einstellungen & Caches", sure=low in RELIABLE_DEVS)
        elif _isdir(os.path.join(e.path, "Saved")) and not NOT_A_GAME.search(e.name) and \
                low not in ("crashreportclient", "epicgameslauncher", "unrealengine", "unrealenginelauncher"):
            out.append((e.path, "Spielstände, Einstellungen & Shader", True))
    for e in _subdirs(docs):
        if e.name.lower() in KNOWN_DEVS and e.name.lower() != "my games":
            add_dev_children(e.path, "Spielstände & Einstellungen")
        elif e.name.lower() != "my games":
            out.append((e.path, "Spielstände & Einstellungen", False))  # nur wenn einem Spiel zuordenbar
    return out


# ------------------------------------------------------------------ Gesamtanalyse
class Games:
    def __init__(self, size_fn):
        self.size_fn = size_fn  # path -> (size, mtime, files)
        self.lock = threading.Lock()
        self.state = "idle"
        self.installed = []
        self.leftovers = []
        self.computed_at = None
        self._installed_paths = []
        self._data_paths = []
        self._leftover_paths = []
        self.error = None

    def refresh_sync(self):
        with self.lock:
            self.state = "running"
        self._run()

    def refresh_async(self):
        with self.lock:
            if self.state == "running":
                return
            self.state = "running"
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self._compute()
            self.state = "done"
        except Exception as exc:  # pragma: no cover
            import traceback
            traceback.print_exc()
            self.error = str(exc)
            self.state = "error"

    def _compute(self):
        now = time.time()
        steam_inst, leftovers = _steam()
        games = steam_inst + _gog() + _epic() + _ubisoft() + _rockstar() + _uninstall_registry() + _xbox()
        # Doppelte entfernen; ein Ordner, der andere Spiele enthält (Launcher), zählt nicht als Spiel
        seen, uniq = set(), []
        for g in sorted(games, key=lambda g: -len(g["path"])):
            p = nc(g["path"])
            if p in seen or any(under(s, p) for s in seen) or len(p.rstrip("\\")) <= 3:
                continue
            seen.add(p)
            uniq.append(g)
        games = uniq
        pf = [nc(x) for x in knowledge.PROGRAM_FILES]
        leftovers = [lo for lo in leftovers if not any(under(nc(lo["path"]), b) for b in pf)]
        for g in games:
            g["al"] = _aliases(g)
            size, mtime, files = self.size_fn(g["path"])
            g["size"] = g.get("size") or size
            g["mtime"] = mtime
            g["data"] = []

        # Daten zuordnen
        leftover_rows = []
        for path, label, sure in _data_candidates():
            name = os.path.basename(path)
            owner = next((g for g in games if _matches(g["al"], name)), None)
            if owner is None:
                parent = os.path.basename(os.path.dirname(path))
                owner = next((g for g in games if _matches(g["al"], parent) and parent.lower() not in KNOWN_DEVS
                              and parent.lower() != "my games"), None)
            if owner is not None:
                size, mtime, files = self.size_fn(path)
                owner["data"].append({"path": path, "name": name, "label": label, "size": size, "mtime": mtime})
            elif sure:
                leftovers.append({"path": path, "name": name, "kind": "data", "label": label})

        for lo in leftovers:
            size, mtime, files = self.size_fn(lo["path"])
            if size <= 0:
                continue
            age = (now - mtime) / 86400 if mtime else 99999
            if lo["kind"] == "install":
                info = knowledge._r("leftover-game", f"Überrest von „{lo['name']}“",
                                    "Installationsordner eines Steam-Spiels, das nicht mehr installiert ist (Steam kennt "
                                    "es nicht mehr). Reine Spieldateien – kann gefahrlos weg.", "safe", None, None, "game")
            elif lo["kind"] == "shader":
                info = knowledge._r("leftover-game", "Shader-Cache eines deinstallierten Spiels",
                                    f"Vorberechnete Grafikdaten der Steam-App {lo.get('appid')}, die nicht mehr "
                                    "installiert ist. Wird nicht mehr gebraucht.", "safe", None, None, "sparkles")
            elif lo["kind"] == "workshop":
                info = knowledge._r("leftover-game", "Workshop-Mods eines deinstallierten Spiels",
                                    f"Mods der Steam-App {lo.get('appid')}, die nicht mehr installiert ist.",
                                    "safe", None, None, "game")
            else:
                info = knowledge._r("leftover-game", f"Daten von „{lo['name']}“ (nicht installiert)",
                                    f"{lo['label']} eines Spiels, das nicht mehr installiert ist. Kann Spielstände "
                                    "enthalten – wenn du es nicht wieder spielen willst, kann es weg "
                                    "(viele Spiele sichern Spielstände zusätzlich in der Cloud).", "likely", None, None, "game")
            info["launcher"] = lo.get("launcher")
            leftover_rows.append({"path": lo["path"], "name": lo["name"], "size": size, "files": files,
                                  "mtime": mtime, "atime": 0, "age": round(age, 1), "info": info,
                                  "score": knowledge.score(info["level"], age, size) + 15})
        leftover_rows.sort(key=lambda r: -r["size"])

        out = []
        for g in games:
            data_size = sum(d["size"] for d in g["data"])
            activity = max([g.get("lastPlayed") or 0] + [d["mtime"] or 0 for d in g["data"]])
            out.append({"id": g["id"], "name": g["name"], "launcher": g["launcher"], "path": g["path"],
                        "appid": g.get("appid"), "size": g["size"], "dataSize": data_size,
                        "total": g["size"] + data_size, "lastPlayed": g.get("lastPlayed") or 0,
                        "lastActive": activity, "data": sorted(g["data"], key=lambda d: -d["size"])})
        out.sort(key=lambda g: -g["total"])
        with self.lock:
            self.installed = out
            self.leftovers = leftover_rows
            self._installed_paths = sorted(((nc(g["path"]), g) for g in out), key=lambda x: -len(x[0]))
            self._data_paths = sorted(((nc(d["path"]), g, d) for g in out for d in g["data"]), key=lambda x: -len(x[0]))
            self._leftover_paths = sorted(((nc(r["path"]), r) for r in leftover_rows), key=lambda x: -len(x[0]))
            self.computed_at = time.time()

    # -------------------------------------------------------------- Abfragen
    def snapshot(self):
        return {"state": self.state, "installed": self.installed, "leftovers": self.leftovers,
                "computedAt": self.computed_at, "error": self.error}

    def lookup(self, path):
        """Gehört der Pfad zu einem Spiel? -> ('installed', game) | ('data', game, d) | ('leftover', row) | None"""
        p = nc(path)
        for lp, row in self._leftover_paths:
            if under(p, lp):
                return ("leftover", row)
        for dp, g, d in self._data_paths:
            if under(p, dp):
                return ("data", g, d)
        for ip, g in self._installed_paths:
            if under(p, ip):
                return ("installed", g)
        return None

    def is_leftover(self, path):
        r = self.lookup(path)
        return bool(r and r[0] == "leftover" and nc(r[1]["path"]) == nc(path))

    def remove(self, path):
        p = nc(path)
        with self.lock:
            self.leftovers = [r for r in self.leftovers if nc(r["path"]) != p]
            self._leftover_paths = [x for x in self._leftover_paths if x[0] != p]
            for g in self.installed:
                g["data"] = [d for d in g["data"] if nc(d["path"]) != p]
