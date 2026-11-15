"""Schnellreinigung: bekannte Müll-Kategorien messen und bereinigen."""
import glob
import os
import stat
import threading
import time

import winapi
from knowledge import HOME, LOCAL, ROAMING, LOCALLOW, WINDIR, PROGRAMDATA, SYSDRIVE, KF

ATTR_REPARSE = 0x400


def nc(p):
    return os.path.normcase(os.path.normpath(p))


def _excluded(path, ex):
    """path liegt in (oder ist) einem der ausgeschlossenen, normalisierten Pfade."""
    if not ex:
        return False
    p = nc(path)
    return any(p == e or p.startswith(e + "\\") for e in ex)


_BASES = None


def _short(path):
    global _BASES
    if _BASES is None:
        _BASES = [(LOCAL, "AppData\\Local"), (ROAMING, "AppData\\Roaming"), (LOCALLOW, "AppData\\LocalLow"),
                  (WINDIR, "Windows"), (PROGRAMDATA, "ProgramData"), (HOME, "~")]
    for base, label in _BASES:
        b = base.rstrip("\\")
        if nc(path).startswith(nc(b) + "\\"):
            return label + path[len(b):]
    return path


def _nice_name(path):
    """z. B. '…\\Google\\Chrome\\User Data\\Default\\Cache' -> 'Chrome › Default › Cache'."""
    parts = [x for x in _short(path).split("\\") if x and x.lower() not in
             ("~", "appdata", "local", "roaming", "locallow", "user data", "microsoft", "windows", "profiles")]
    return " › ".join(parts[-3:]) or os.path.basename(path)


def _item(path, size, mtime, is_dir, count, name=None):
    return {"path": path, "name": name or os.path.basename(path), "sub": _short(path), "size": size,
            "mtime": mtime, "isDir": is_dir, "count": count}


def _t(path, min_age=0, admin=False, mode="contents"):
    return {"path": path, "min_age": min_age, "admin": admin, "mode": mode}


def _browser(base):
    out = []
    for sub in ("Cache", "Code Cache", "GPUCache", "DawnCache", "DawnGraphiteCache", "DawnWebGPUCache",
                "ShaderCache", "GrShaderCache"):
        out.append(_t(os.path.join(base, "User Data", "*", sub)))
        out.append(_t(os.path.join(base, "User Data", sub)))
    return out


def categories():
    L, R, W = LOCAL, ROAMING, WINDIR
    dl = KF.get("downloads") or os.path.join(HOME, "Downloads")
    return [
        {"id": "temp", "name": "Temporäre Dateien", "icon": "sparkles", "level": "safe", "default": True, "detail": "children",
         "method": "delete",
         "text": "Zwischendateien von Programmen, Installern und Windows. Dateien, die jünger als 24 Stunden "
                 "sind oder gerade benutzt werden, bleiben automatisch erhalten.",
         "targets": [_t(os.path.join(L, "Temp"), 24), _t(os.path.join(W, "Temp"), 24, True)]},
        {"id": "browser", "name": "Browser-Cache", "icon": "globe", "level": "safe", "default": True,
         "method": "delete",
         "text": "Zwischengespeicherte Webseiten-Bilder und Skripte von Chrome, Edge, Brave, Opera und Firefox. "
                 "Logins, Passwörter, Lesezeichen und Verlauf bleiben erhalten. Am besten Browser vorher schließen.",
         "targets": _browser(os.path.join(L, "Google", "Chrome"))
         + _browser(os.path.join(L, "Microsoft", "Edge"))
         + _browser(os.path.join(L, "BraveSoftware", "Brave-Browser"))
         + _browser(os.path.join(L, "Vivaldi"))
         + [_t(os.path.join(L, "Mozilla", "Firefox", "Profiles", "*", "cache2")),
            _t(os.path.join(L, "Opera Software", "Opera Stable", "Cache")),
            _t(os.path.join(L, "Opera Software", "Opera GX Stable", "Cache")),
            _t(os.path.join(L, "Microsoft", "Windows", "INetCache"))]},
        {"id": "apps", "name": "App-Caches", "icon": "box", "level": "safe", "default": True,
         "method": "delete",
         "text": "Zwischenspeicher von Discord, Spotify, VS Code, Teams, Slack und Steam-Webansichten. "
                 "Die Apps bauen ihn bei Bedarf neu auf. Geöffnete Apps vorher schließen.",
         "targets": [_t(os.path.join(R, a, s)) for a in ("discord", "Slack", "Code", "Microsoft\\Teams",
                                                         "Notion", "Figma", "WhatsApp")
                     for s in ("Cache", "Code Cache", "GPUCache", "CachedData", "CachedExtensionVSIXs")]
         + [_t(os.path.join(L, "Spotify", "Data")), _t(os.path.join(L, "Steam", "htmlcache")),
            _t(os.path.join(L, "EpicGamesLauncher", "Saved", "webcache*"))]},
        {"id": "shader", "name": "Grafik-Shader-Cache", "icon": "cpu", "level": "safe", "default": False,
         "method": "delete",
         "text": "Vorberechnete Shader von DirectX und Grafiktreibern (AMD/NVIDIA/Intel). Wird automatisch neu "
                 "erzeugt – Spiele können beim ersten Start kurz ruckeln. Sinnvoll nach Treiber-Updates.",
         "targets": [_t(os.path.join(L, "D3DSCache")), _t(os.path.join(L, "NVIDIA", "DXCache")),
                     _t(os.path.join(L, "NVIDIA", "GLCache")), _t(os.path.join(L, "AMD", "DxCache")),
                     _t(os.path.join(L, "AMD", "DxcCache")), _t(os.path.join(L, "AMD", "GLCache")),
                     _t(os.path.join(L, "AMD", "VkCache")), _t(os.path.join(L, "Intel", "ShaderCache")),
                     _t(os.path.join(LOCALLOW, "NVIDIA", "PerDriverVersion", "DXCache"))]},
        {"id": "thumbs", "name": "Miniaturansichten", "icon": "image", "level": "safe", "default": True,
         "method": "delete",
         "text": "Vorschaubilder, die der Explorer für Fotos und Videos speichert. Werden beim nächsten Öffnen "
                 "eines Ordners neu erstellt. Gerade benutzte Dateien werden übersprungen.",
         "targets": [_t(os.path.join(L, "Microsoft", "Windows", "Explorer", "thumbcache_*.db"), mode="file"),
                     _t(os.path.join(L, "Microsoft", "Windows", "Explorer", "iconcache_*.db"), mode="file")]},
        {"id": "crash", "name": "Absturzberichte & Speicherabbilder", "icon": "alert", "level": "safe", "detail": "children",
         "default": True, "method": "delete",
         "text": "Fehlerberichte und Speicherabbilder nach Programm- oder Systemabstürzen. Nur für die "
                 "Fehlersuche durch Entwickler gedacht.",
         "targets": [_t(os.path.join(L, "CrashDumps")),
                     _t(os.path.join(L, "Microsoft", "Windows", "WER", "ReportArchive")),
                     _t(os.path.join(L, "Microsoft", "Windows", "WER", "ReportQueue")),
                     _t(os.path.join(PROGRAMDATA, "Microsoft", "Windows", "WER", "ReportArchive"), admin=True),
                     _t(os.path.join(PROGRAMDATA, "Microsoft", "Windows", "WER", "ReportQueue"), admin=True),
                     _t(os.path.join(W, "Minidump"), admin=True),
                     _t(os.path.join(W, "LiveKernelReports"), admin=True),
                     _t(os.path.join(W, "MEMORY.DMP"), admin=True, mode="file")]},
        {"id": "winupdate", "name": "Windows-Update-Reste", "icon": "refresh", "level": "safe", "default": True,
         "method": "delete",
         "text": "Bereits installierte Update-Downloads und der Zustelloptimierungs-Cache. Windows lädt bei "
                 "Bedarf neu herunter. Benötigt Administratorrechte.",
         "targets": [_t(os.path.join(W, "SoftwareDistribution", "Download"), 24, True),
                     _t(os.path.join(W, "ServiceProfiles", "NetworkService", "AppData", "Local", "Microsoft",
                                     "Windows", "DeliveryOptimization", "Cache"), 0, True)]},
        {"id": "dev", "name": "Entwickler-Caches", "icon": "code", "level": "likely", "default": False,
         "method": "delete",
         "text": "Paket-Downloads von npm, pip, uv, Yarn, pnpm, NuGet und Gradle. Werden beim nächsten Build "
                 "automatisch neu geladen (braucht dann Internet und etwas Zeit).",
         "targets": [_t(os.path.join(L, "npm-cache")), _t(os.path.join(L, "pip", "cache")),
                     _t(os.path.join(L, "uv", "cache")), _t(os.path.join(L, "Yarn", "Cache")),
                     _t(os.path.join(L, "pnpm", "store")), _t(os.path.join(L, "NuGet", "v3-cache")),
                     _t(os.path.join(L, "NuGet", "Cache")), _t(os.path.join(HOME, ".nuget", "packages")),
                     _t(os.path.join(HOME, ".gradle", "caches"))]},
        {"id": "installers", "name": "Alte Installer in Downloads", "icon": "download", "level": "likely",
         "default": False, "method": "recycle",
         "text": "Installationsprogramme (.exe, .msi, .msix) im Download-Ordner, die älter als 30 Tage sind. "
                 "Die Programme sind längst installiert – die Installer kannst du jederzeit neu laden. "
                 "Landen zur Sicherheit im Papierkorb.",
         "targets": [_t(os.path.join(dl, "*" + e), 24 * 30, mode="file") for e in (".exe", ".msi", ".msix")]},
        {"id": "recyclebin", "name": "Papierkorb", "icon": "trash", "level": "likely", "default": False,
         "method": "special",
         "text": "Bereits gelöschte Dateien belegen weiter Platz, bis der Papierkorb geleert wird. "
                 "Achtung: Danach lassen sie sich nicht mehr wiederherstellen.",
         "targets": []},
    ]


def _iter_targets(target):
    pattern = target["path"]
    paths = glob.glob(pattern) if any(c in pattern for c in "*?[") else [pattern]
    for p in paths:
        if target["mode"] == "file":
            if os.path.isfile(p):
                yield p, False
        elif os.path.isdir(p):
            yield p, True


def _walk_files(top):
    """(Dateien [(pfad, größe, mtime)], Ordner [pfad], verweigert)"""
    files, dirs, denied = [], [], False
    stack = [top]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if st.st_file_attributes & 0x10:
                        if st.st_file_attributes & ATTR_REPARSE:
                            continue
                        dirs.append(e.path)
                        stack.append(e.path)
                    else:
                        files.append((e.path, st.st_size, st.st_mtime))
        except PermissionError:
            denied = True
        except OSError:
            pass
    return files, dirs, denied


def _file_stat(p):
    """Größe/mtime auch für gesperrte Dateien über das Verzeichnislisting."""
    try:
        with os.scandir(os.path.dirname(p)) as it:
            for e in it:
                if e.name.lower() == os.path.basename(p).lower():
                    st = e.stat(follow_symlinks=False)
                    return st.st_size, st.st_mtime
    except OSError:
        pass
    return 0, 0


class Junk:
    def __init__(self):
        self.cats = categories()
        self.state = {c["id"]: {"size": 0, "files": 0, "needsAdmin": False, "measured": False} for c in self.cats}
        self.measuring = False
        self.lock = threading.Lock()
        self.extra = {}

    def by_id(self, cid):
        return next((c for c in self.cats if c["id"] == cid), None)

    def measure_all(self):
        with self.lock:
            if self.measuring:
                return
            self.measuring = True
        try:
            admin = winapi.is_admin()
            for c in self.cats:
                self.state[c["id"]] = self._measure(c, admin)
            self.extra = self._extras()
        finally:
            self.measuring = False

    def _measure(self, cat, admin):
        if cat["id"] == "recyclebin":
            info = winapi.recycle_bin_info()
            return {"size": info["size"], "files": info["items"], "needsAdmin": False, "measured": True}
        total = files = 0
        needs_admin = False
        now = time.time()
        for t in cat["targets"]:
            cutoff = now - t["min_age"] * 3600
            for p, is_dir in _iter_targets(t):
                if is_dir:
                    fl, _, denied = _walk_files(p)
                    if denied and t["admin"] and not admin:
                        needs_admin = True
                    for _, sz, m in fl:
                        if m <= cutoff:
                            total += sz
                            files += 1
                else:
                    sz, m = _file_stat(p)
                    if m <= cutoff:
                        total += sz
                        files += 1
            if t["admin"] and not admin and os.path.exists(t["path"].split("*")[0]):
                try:
                    os.listdir(t["path"]) if t["mode"] != "file" else None
                except PermissionError:
                    needs_admin = True
                except OSError:
                    pass
        return {"size": total, "files": files, "needsAdmin": needs_admin, "measured": True}

    def _extras(self):
        """Infos, die nicht automatisch bereinigt werden (Hinweise)."""
        out = []
        sysroot = SYSDRIVE
        try:
            with os.scandir(sysroot) as it:
                for e in it:
                    n = e.name.lower()
                    if n == "hiberfil.sys":
                        out.append({"id": "hiberfil", "name": "Ruhezustandsdatei (hiberfil.sys)",
                                    "size": e.stat(follow_symlinks=False).st_size,
                                    "text": "Reserviert Platz für den Ruhezustand/Schnellstart. Wenn du ihn nicht "
                                            "nutzt: Eingabeaufforderung als Administrator öffnen und "
                                            "„powercfg /h off“ eingeben.", "action": None})
                    elif n == "windows.old":
                        fl, _, _ = _walk_files(e.path)
                        out.append({"id": "winold", "name": "Vorherige Windows-Installation (Windows.old)",
                                    "size": sum(s for _, s, _ in fl),
                                    "text": "Backup der alten Windows-Version. Entfernen über Einstellungen › "
                                            "System › Speicher › Temporäre Dateien › „Vorherige "
                                            "Windows-Installation(en)“.", "action": "storage"})
        except OSError:
            pass
        return out

    def snapshot(self):
        out = []
        for c in self.cats:
            s = self.state[c["id"]]
            out.append({k: c[k] for k in ("id", "name", "icon", "level", "default", "method", "text")} | s)
        return {"categories": out, "measuring": self.measuring, "extras": self.extra}

    # ------------------------------------------------------------ Einzelne Einträge
    def items(self, cid, limit=3000):
        """Was steckt hinter einer Kategorie? Liste der Einträge, die bereinigt würden."""
        cat = self.by_id(cid)
        if not cat:
            return [], 0
        if cid == "recyclebin":
            items = winapi.recycle_bin_items()
            return items[:limit], len(items)
        out = []
        now = time.time()
        detail = cat.get("detail", "target")
        for t in cat["targets"]:
            cutoff = now - t["min_age"] * 3600
            for p, is_dir in _iter_targets(t):
                if not is_dir:
                    sz, m = _file_stat(p)
                    if m <= cutoff:
                        out.append(_item(p, sz, m, False, 1))
                    continue
                if detail == "children":
                    try:
                        entries = list(os.scandir(p))
                    except OSError:
                        continue
                    for e in entries:
                        try:
                            st = e.stat(follow_symlinks=False)
                        except OSError:
                            continue
                        if st.st_file_attributes & 0x10:
                            if st.st_file_attributes & ATTR_REPARSE:
                                continue
                            fl, _, _ = _walk_files(e.path)
                            ok = [f for f in fl if f[2] <= cutoff]
                            if ok:
                                out.append(_item(e.path, sum(f[1] for f in ok), max(f[2] for f in ok), True, len(ok)))
                        elif st.st_mtime <= cutoff:
                            out.append(_item(e.path, st.st_size, st.st_mtime, False, 1))
                else:
                    fl, _, _ = _walk_files(p)
                    ok = [f for f in fl if f[2] <= cutoff]
                    if ok:
                        out.append(_item(p, sum(f[1] for f in ok), max(f[2] for f in ok), True, len(ok),
                                         _nice_name(p)))
        out.sort(key=lambda x: -x["size"])
        return out[:limit], len(out)

    # ------------------------------------------------------------ Bereinigen
    def clean(self, ids, exclude=None):
        results = []
        admin = winapi.is_admin()
        exclude = exclude or {}
        for cid in ids:
            cat = self.by_id(cid)
            if not cat:
                continue
            ex = [nc(p) for p in exclude.get(cid, []) if isinstance(p, str)]
            if cid == "recyclebin":
                before = winapi.recycle_bin_info()
                if ex:
                    keep = set(ex)
                    for it in winapi.recycle_bin_items():
                        if nc(it["path"]) not in keep:
                            winapi.recycle_bin_delete(it["path"])
                    ok = True
                else:
                    ok = winapi.empty_recycle_bin()
                after = winapi.recycle_bin_info()
                results.append({"id": cid, "freed": max(0, before["size"] - after["size"]),
                                "removed": max(0, before["items"] - after["items"]), "skipped": 0, "ok": ok})
                self.state[cid] = self._measure(cat, admin)
                continue
            freed = skipped = removed = 0
            now = time.time()
            for t in cat["targets"]:
                cutoff = now - t["min_age"] * 3600
                for p, is_dir in _iter_targets(t):
                    if _excluded(p, ex):
                        continue
                    if is_dir:
                        fl, dirs, _ = _walk_files(p)
                    else:
                        sz, m = _file_stat(p)
                        fl, dirs = [(p, sz, m)], []
                    for fp, sz, m in fl:
                        if m > cutoff or (ex and _excluded(fp, ex)):
                            continue
                        if self._delete_file(fp, cat["method"] == "recycle"):
                            freed += sz
                            removed += 1
                        else:
                            skipped += 1
                    for d in sorted(dirs, key=len, reverse=True):
                        if ex and _excluded(d, ex):
                            continue
                        try:
                            os.rmdir(d)
                        except OSError:
                            pass
            results.append({"id": cid, "freed": freed, "removed": removed, "skipped": skipped, "ok": True})
            self.state[cid] = self._measure(cat, admin)
        return results

    @staticmethod
    def _delete_file(p, recycle):
        if recycle:
            return winapi.move_to_recycle_bin(p) and not os.path.exists(p)
        try:
            os.remove(p)
            return True
        except PermissionError:
            try:
                os.chmod(p, stat.S_IWRITE)
                os.remove(p)
                return True
            except OSError:
                return False
        except FileNotFoundError:
            return True
        except OSError:
            return False
