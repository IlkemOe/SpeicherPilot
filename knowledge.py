"""Wissen über typische Windows-Ordner und Dateitypen: Erklärung, Empfehlung, Schutz."""
import os
import re
import threading

import winapi

HOME = os.path.expanduser("~")
LOCAL = os.environ.get("LOCALAPPDATA") or os.path.join(HOME, "AppData", "Local")
ROAMING = os.environ.get("APPDATA") or os.path.join(HOME, "AppData", "Roaming")
LOCALLOW = os.path.join(HOME, "AppData", "LocalLow")
WINDIR = os.environ.get("SystemRoot") or r"C:\Windows"
SYSDRIVE = (os.environ.get("SystemDrive") or "C:") + "\\"
PROGRAMDATA = os.environ.get("ProgramData") or r"C:\ProgramData"
PROGRAM_FILES = [p for p in {os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
                             os.environ.get("ProgramW6432"), r"C:\Program Files",
                             r"C:\Program Files (x86)"} if p]
KF = winapi.known_folders()
ONEDRIVE = [p for p in {os.environ.get("OneDrive"), os.environ.get("OneDriveConsumer"),
                        os.environ.get("OneDriveCommercial")} if p]
APP_DIR = os.path.dirname(os.path.abspath(__file__))

LEVELS = {
    "safe": "Sicher löschbar",
    "likely": "Empfohlen zu löschen",
    "review": "Bitte prüfen",
    "uninstall": "Deinstallieren",
    "keep": "Behalten",
}


def nc(p):
    return os.path.normcase(os.path.normpath(p)) if p else ""


def under(p, base):
    """p (normalisiert) liegt in base oder ist base."""
    b = nc(base).rstrip("\\")
    return p == b or p.startswith(b + "\\")


def rel_first(p, base):
    """Erste Pfadkomponente unterhalb von base (Originalschreibweise wird nicht benötigt)."""
    b = nc(base).rstrip("\\")
    rest = p[len(b) + 1:]
    return rest.split("\\", 1)[0] if rest else ""


def first_component(path, base):
    """Wie rel_first, aber mit Originalschreibweise aus path."""
    b = os.path.normpath(base).rstrip("\\")
    rest = os.path.normpath(path)[len(b) + 1:]
    return rest.split("\\", 1)[0] if rest else ""


# --------------------------------------------------------------- Container
_CONTAINERS = {nc(p) for p in [
    HOME, os.path.dirname(HOME), os.path.join(os.path.dirname(HOME), "Public"),
    os.path.join(HOME, "AppData"), LOCAL, ROAMING, LOCALLOW, PROGRAMDATA,
    os.path.join(LOCAL, "Programs"), os.path.join(LOCAL, "Packages"),
    os.path.join(LOCAL, "Microsoft"), os.path.join(ROAMING, "Microsoft"),
    os.path.join(HOME, ".cache"), os.path.join(HOME, "source"), os.path.join(HOME, "source", "repos"),
    *PROGRAM_FILES, *KF.values(), *ONEDRIVE,
] if p}
_CONTAINER_NAMES = {"steamapps", "common", "steamlibrary", "epic games", "games", "spiele",
                    "xboxgames", "gog games", "gog galaxy", "projects", "projekte", "repos",
                    "program files", "program files (x86)", "programme"}


def is_container(path):
    """Sammelordner werden nicht selbst empfohlen, sondern ihr Inhalt wird einzeln betrachtet."""
    p = nc(path)
    if len(p.rstrip("\\")) <= 2 or p.endswith(":\\"):
        return True
    if p in _CONTAINERS:
        return True
    return os.path.basename(p) in _CONTAINER_NAMES


# --------------------------------------------------------------- installierte Programme
_installed = None
_installed_lock = threading.Lock()


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def installed_tokens():
    global _installed
    with _installed_lock:
        if _installed is None:
            toks = set()
            try:
                for n in winapi.installed_programs():
                    t = _norm(n)
                    if len(t) >= 3:
                        toks.add(t)
            except Exception:
                pass
            for base in PROGRAM_FILES + [os.path.join(LOCAL, "Programs")]:
                try:
                    for e in os.scandir(base):
                        t = _norm(e.name)
                        if len(t) >= 3:
                            toks.add(t)
                except OSError:
                    pass
            _installed = toks
        return _installed


def looks_installed(vendor):
    v = _norm(vendor)
    if len(v) < 3:
        return True  # zu kurz zum Raten -> lieber "installiert" annehmen
    for t in installed_tokens():
        if v in t or t in v:
            return True
    return False


_SYSTEM_APPDATA = {"microsoft", "packages", "temp", "programs", "comms", "connecteddevicesplatform",
                   "d3dscache", "placeholdertilelogofolder", "publishers", "virtualstore", "crashdumps",
                   "microsoft_corporation", "windows", "history", "elevateddiagnostics", "peerdistrepub",
                   "fontcache", "iconcache.db", "githubdesktop", "squirreltemp", "npm-cache", "pip",
                   "nvidia", "nvidia corporation", "amd", "intel", "realtek", "package cache", "toastnotificationmanagercompat"}

# --------------------------------------------------------------- Regeln
_CACHE_NAMES = re.compile(
    r"^(cache|caches|cache2|cache_data|gpucache|code cache|shadercache|shader cache|shadercache\d*|"
    r"dxcache|glcache|dxccache|vkcache|d3dscache|htmlcache|webcache.*|cacheddata|cachestorage|"
    r"inetcache|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.parcel-cache|\.next|\.nuxt|"
    r"\.turbo|\.angular|crashpad|crashdumps|logs?)$")
_EMULATORS = ("yuzu", "ryujinx", "suyu", "sudachi", "citron", "cemu", "dolphin emulator", "rpcs3",
              "ppsspp", "pcsx2", "duckstation", "retroarch", "xenia")
_EMU_SAVES = ("nand", "save", "saves", "bis", "sdmc", "mlc01", "memcards", "savedata", "user\\save", "states")
_DEV_CACHES = [
    (os.path.join(HOME, ".gradle"), "Gradle-Cache (Java/Android)"),
    (os.path.join(HOME, ".m2"), "Maven-Paketcache (Java)"),
    (os.path.join(HOME, ".nuget"), "NuGet-Pakete (.NET)"),
    (os.path.join(LOCAL, "NuGet"), "NuGet-Cache (.NET)"),
    (os.path.join(LOCAL, "npm-cache"), "npm-Cache (Node.js)"),
    (os.path.join(ROAMING, "npm-cache"), "npm-Cache (Node.js)"),
    (os.path.join(LOCAL, "pip"), "pip-Cache (Python)"),
    (os.path.join(LOCAL, "uv"), "uv-Cache (Python)"),
    (os.path.join(LOCAL, "Yarn"), "Yarn-Cache (Node.js)"),
    (os.path.join(LOCAL, "pnpm"), "pnpm-Speicher (Node.js)"),
    (os.path.join(HOME, ".cargo", "registry"), "Cargo-Registry (Rust)"),
    (os.path.join(HOME, "go", "pkg", "mod"), "Go-Modulcache"),
]
_AI = [os.path.join(HOME, ".cache", "huggingface"), os.path.join(HOME, ".ollama"),
       os.path.join(HOME, ".cache", "torch"), os.path.join(HOME, ".cache", "lm-studio"),
       os.path.join(HOME, ".lmstudio")]

VIDEO = {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".m4v", ".webm", ".flv", ".ts", ".mts", ".m2ts", ".mpg", ".mpeg"}
AUDIO = {".wav", ".flac", ".mp3", ".aac", ".m4a", ".ogg", ".aiff"}
IMAGE_DISK = {".iso", ".img", ".dmg", ".bin", ".cue", ".wim", ".esd"}
ARCHIVE = {".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".zst", ".cab"}
VM = {".vhd", ".vhdx", ".vmdk", ".vdi", ".qcow2", ".avhdx", ".hdd"}
INSTALLER = {".exe", ".msi", ".msix", ".msixbundle", ".appx", ".appxbundle"}
AI_MODEL = {".safetensors", ".ckpt", ".gguf", ".pt", ".pth", ".onnx", ".bin", ".h5", ".pb"}
CONSOLE = {".nsp", ".xci", ".nsz", ".xcz", ".wbfs", ".rvz", ".wua", ".chd", ".pkg"}
GAME_DATA = {".pak", ".vpk", ".ucas", ".utoc", ".bsa", ".ba2", ".forge", ".rpf", ".arc", ".wad", ".big", ".dat", ".assets", ".bundle", ".blob"}
PHOTO_RAW = {".psd", ".raw", ".cr2", ".cr3", ".nef", ".arw", ".dng", ".tif", ".tiff"}
DOC_DB = {".pst", ".ost"}


PICTURES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif", ".bmp", ".svg"} | PHOTO_RAW
MODELS_3D = {".stl", ".obj", ".fbx", ".blend", ".blend1", ".3mf", ".lys", ".ztl", ".zpr", ".glb", ".gltf",
             ".max", ".ma", ".mb", ".ctb", ".chitubox", ".gcode", ".step", ".stp", ".3ds", ".dae"}
DOCS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".odt", ".ods", ".rtf", ".epub", ".csv"}
PROGRAMS = {".exe", ".dll", ".sys", ".msi", ".so", ".pyd", ".lib", ".jar"}
CODE = {".js", ".ts", ".py", ".pyc", ".java", ".class", ".cs", ".cpp", ".c", ".h", ".json", ".map", ".rs",
        ".go", ".php", ".html", ".css", ".xml", ".yml", ".yaml", ".lock", ".node"}
_EXT_GROUPS = [("Videos", VIDEO), ("Bilder", PICTURES), ("3D-Modelle", MODELS_3D), ("Audio", AUDIO),
               ("Archive", ARCHIVE), ("Disk-Abbilder", IMAGE_DISK - {".bin"}), ("Spieldaten", GAME_DATA | CONSOLE),
               ("KI-Modelle", AI_MODEL - {".bin"}), ("Programme", PROGRAMS), ("Dokumente", DOCS),
               ("Code", CODE), ("Virtuelle Festplatten", VM), ("Logs & Temp", {".log", ".tmp", ".dmp", ".etl", ".bak"})]


def ext_group(ext):
    for label, exts in _EXT_GROUPS:
        if ext in exts:
            return label
    return "Sonstiges"


def _r(kind, title, text, level, protect=None, action=None, icon="folder"):
    return {"kind": kind, "title": title, "text": text, "level": level,
            "levelLabel": LEVELS[level], "protect": protect, "action": action, "icon": icon}


def _system_rules(p, name):
    if under(p, WINDIR):
        return _r("system", "Windows-Systemdateien", "Teil von Windows. Hier wird nie direkt gelöscht – "
                  "nutze dafür die Schnellreinigung oder die Windows-Speichereinstellungen.", "keep",
                  "Windows-Systemordner", "storage", "shield")
    if under(p, os.path.join(SYSDRIVE, "Windows.old")):
        return _r("system", "Vorherige Windows-Installation",
                  "Backup deiner alten Windows-Version nach einem großen Update. Wenn alles läuft, kannst du "
                  "sie gefahrlos über Einstellungen › System › Speicher › Temporäre Dateien entfernen.",
                  "likely", "Bitte über die Windows-Speichereinstellungen entfernen", "storage", "shield")
    if name in ("$recycle.bin", "system volume information", "recovery", "$windows.~bt", "$windows.~ws",
                "$winreagent", "msocache", "$sysreset", "config.msi"):
        return _r("system", "Geschützter Systembereich", "Wird von Windows selbst verwaltet.", "keep",
                  "Geschützter Systembereich", None, "shield")
    if under(p, APP_DIR):
        return _r("system", "SpeicherPilot", "Diese Anwendung selbst.", "keep", "SpeicherPilot selbst", None, "shield")
    return None


GAME_HOOK = None  # wird von speicherpilot.py gesetzt: Pfad -> Spielzuordnung
GAME_ACTIVE_DAYS = 180


def _fmt_bytes(b):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024 or unit == "TB":
            return (f"{b:.1f}".replace(".", ",") if unit in ("GB", "TB") else f"{b:.0f}") + " " + unit
        b /= 1024


def _game_info(path, is_file=False):
    if GAME_HOOK is None:
        return None
    try:
        r = GAME_HOOK(path)
    except Exception:
        return None
    if not r:
        return None
    if r[0] == "leftover":
        info = dict(r[1]["info"])
        if is_file:
            info["title"] += " – Datei"
        return info
    g = r[1]
    import time as _t
    active = g.get("lastActive") and (_t.time() - g["lastActive"]) / 86400 < GAME_ACTIVE_DAYS
    if r[0] == "data":
        d = r[2]
        return _r("saves", f"Daten von „{g['name']}“ (installiert)",
                  f"{d['label']} des installierten Spiels „{g['name']}“ – werden sehr wahrscheinlich noch "
                  "gebraucht. Erst löschen, wenn du das Spiel deinstalliert hast.", "keep", None, None, "game")
    steam = g["launcher"] == "Steam"
    text = (f"Gehört zum installierten Spiel „{g['name']}“ ({g['launcher']}) und wird gebraucht, solange es "
            "installiert ist. " + ("Einzelne Spieldateien nie löschen – das beschädigt das Spiel. " if is_file else "")
            + ("Du hast es länger nicht gespielt: " if g.get("lastActive") and not active else "Spielst du es nicht mehr: ")
            + f"über {g['launcher']} deinstallieren gibt {_fmt_bytes(g['total'])} frei.")
    info = _r("game", f"Installiertes Spiel „{g['name']}“", text, "keep" if active or not g.get("lastActive")
              else "uninstall", f"Installiertes Spiel – bitte über {g['launcher']} deinstallieren",
              "steam-uninstall" if steam and g.get("appid") else "apps", "game")
    info["appid"] = g.get("appid")
    return info


def classify_folder(path, age_days=0, size=0):
    p = nc(path)
    name = os.path.basename(p.rstrip("\\"))
    orig_name = os.path.basename(os.path.normpath(path)) or path

    r = _system_rules(p, name)
    if r:
        return r
    r = _game_info(path)
    if r:
        return r

    # Steam-Sonderordner
    if "\\steamapps\\" in p + "\\":
        if "\\steamapps\\downloading" in p or "\\steamapps\\temp" in p:
            return _r("game", "Unfertiger Steam-Download",
                      "Ein laufendes oder abgebrochenes Spiel-Update. Brauchst du es nicht mehr, entferne es in Steam "
                      "unter „Downloads“ bzw. deinstalliere das Spiel – sonst lädt Steam es erneut herunter.",
                      "review", None, "steam", "download")
        if "\\steamapps\\shadercache" in p:
            return _r("cache", "Steam-Shader-Cache", "Vorab geladene Grafik-Shader für Steam-Spiele. Werden bei "
                      "Bedarf neu erzeugt.", "safe", None, None, "sparkles")
        if "\\steamapps\\workshop" in p:
            return _r("game", "Steam-Workshop-Mods", "Abonnierte Mods. Beende das Abo im Workshop, dann entfernt "
                      "Steam die Dateien selbst.", "review", None, "steam", "game")

    # Programme
    for pf in PROGRAM_FILES:
        if under(p, pf):
            if "\\steamapps\\common\\" in p + "\\":
                game = _after(path, "steamapps\\common")
                return _r("game", f"Steam-Spiel „{game}“",
                          "Ein über Steam installiertes Spiel. Spielstände liegen meist in der Steam-Cloud, "
                          "das Spiel kann jederzeit neu geladen werden. Deinstalliere es in Steam "
                          "(Bibliothek › Rechtsklick › Verwalten › Deinstallieren).",
                          "uninstall", "Installierte Spiele bitte über Steam deinstallieren", "steam", "game")
            prog = first_component(path, pf)
            return _r("program", f"Programm „{prog}“",
                      "Installiertes Programm. Programme nie einfach löschen – über Einstellungen › Apps "
                      "deinstallieren, damit auch Registry-Einträge und Verknüpfungen verschwinden.",
                      "uninstall", "Programme bitte über Einstellungen › Apps deinstallieren", "apps", "package")
    if under(p, PROGRAMDATA):
        sub = first_component(path, PROGRAMDATA)
        if sub.lower() == "package cache":
            return _r("system", "Installer-Cache",
                      "Kopien von Installationspaketen (z. B. Visual Studio). Werden für Reparatur und "
                      "Deinstallation gebraucht – nicht manuell löschen.", "keep",
                      "Wird von Installern benötigt", None, "shield")
        return _r("program", f"Programmdaten „{sub}“",
                  "Gemeinsame Daten installierter Programme für alle Benutzer. Werden beim Deinstallieren "
                  "des Programms entfernt.", "keep", "Gemeinsame Programmdaten", "apps", "package")
    if under(p, os.path.join(LOCAL, "Packages")):
        return _r("program", "Daten einer Store-App",
                  "Gehört zu einer App aus dem Microsoft Store. Über Einstellungen › Apps zurücksetzen oder "
                  "deinstallieren statt löschen.", "keep", "Store-App-Daten", "apps", "package")

    # Caches & Temp
    if _CACHE_NAMES.match(name) and name not in ("logs", "log"):
        return _r("cache", "Zwischenspeicher (Cache)",
                  "Temporär gespeicherte Daten, die Programme bei Bedarf automatisch neu erstellen. "
                  "Löschen ist unbedenklich – das Programm startet höchstens einmal etwas langsamer.",
                  "safe", None, None, "sparkles")
    if name in ("logs", "log"):
        return _r("logs", "Protokolldateien",
                  "Logdateien, die Programme zur Fehlersuche schreiben. Für den Alltag nicht nötig.",
                  "safe" if age_days > 30 else "likely", None, None, "doc")
    if under(p, os.path.join(LOCAL, "Temp")) or name in ("temp", "tmp"):
        return _r("temp", "Temporäre Dateien",
                  "Zwischendateien von Installationen und Programmen. Kann gelöscht werden.",
                  "safe", None, None, "sparkles")

    # Emulatoren
    for emu in _EMULATORS:
        if f"\\{emu}\\" in p + "\\":
            tail = p.split(f"\\{emu}\\", 1)[1] if f"\\{emu}\\" in p else ""
            if "shader" in tail or "cache" in tail:
                return _r("cache", "Shader-Cache des Emulators",
                          "Vorkompilierte Grafik-Shader. Werden beim Spielen neu erzeugt (anfangs evtl. kurze Ruckler).",
                          "safe", None, None, "sparkles")
            if any(f"\\{s}" in "\\" + tail or tail == s for s in _EMU_SAVES):
                return _r("saves", "Emulator: Spielstände/Systemdaten",
                          "Kann deine Spielstände enthalten. Nur löschen, wenn du sie sicher nicht mehr brauchst "
                          "oder vorher eine Sicherung gemacht hast.", "keep", None, None, "game")
            return _r("game", f"Emulator-Daten ({emu.title()})",
                      "Einstellungen, Mods oder Spieldaten eines Emulators. Prüfe, ob Spielstände enthalten sind.",
                      "review", None, None, "game")

    # Spiele außerhalb von Program Files
    if "\\steamapps\\common\\" in p:
        game = _after(path, "steamapps\\common")
        return _r("game", f"Steam-Spiel „{game}“",
                  "Ein über Steam installiertes Spiel. Am saubersten über Steam deinstallieren – "
                  "Spielstände liegen meist in der Steam-Cloud.", "uninstall", None, "steam", "game")
    for launcher, lname in (("\\epic games\\", "Epic Games"), ("\\gog games\\", "GOG"),
                            ("\\xboxgames\\", "Xbox"), ("\\ea games\\", "EA"), ("\\ubisoft game launcher\\games\\", "Ubisoft")):
        if launcher in p + "\\" and not p.endswith(launcher.rstrip("\\")):
            return _r("game", f"{lname}-Spiel „{orig_name}“",
                      f"Über den {lname}-Launcher installiertes Spiel. Bitte dort deinstallieren.",
                      "uninstall", None, None, "game")

    # Entwickler
    if name == "node_modules":
        return _r("dev", "Node.js-Abhängigkeiten",
                  "Heruntergeladene Pakete eines JavaScript-Projekts. Lassen sich im Projektordner mit "
                  "„npm install“ jederzeit neu erzeugen.", "safe" if age_days > 30 else "likely", None, None, "code")
    if name in (".venv", "venv", "env", ".env") and os.path.isfile(os.path.join(path, "pyvenv.cfg")):
        return _r("dev", "Python-Umgebung",
                  "Virtuelle Python-Umgebung eines Projekts. Kann mit „pip install -r requirements.txt“ neu "
                  "erstellt werden.", "likely", None, None, "code")
    if os.path.isfile(os.path.join(path, "CACHEDIR.TAG")):
        return _r("dev", "Build-Ausgabe / Cache",
                  "Der Ordner ist ausdrücklich als Cache markiert (CACHEDIR.TAG) und wird beim nächsten "
                  "Build neu erzeugt.", "safe", None, None, "code")
    for base, label in _DEV_CACHES:
        if under(p, base):
            return _r("dev", label, "Zwischengespeicherte Downloads von Entwickler-Werkzeugen. Werden bei "
                      "Bedarf automatisch neu geladen.", "safe", None, None, "code")
    if under(p, os.path.join(HOME, ".android", "avd")):
        return _r("dev", "Android-Emulator-Geräte", "Virtuelle Android-Geräte. Über den Android Studio "
                  "Device Manager löschen, falls nicht mehr gebraucht.", "review", None, None, "code")
    if under(p, os.path.join(LOCAL, "Android", "Sdk")):
        return _r("dev", "Android SDK", "Entwicklerwerkzeuge für Android. Nur löschen, wenn du keine "
                  "Android-Apps mehr entwickelst.", "review", None, None, "code")
    if name == ".git":
        return _r("dev", "Git-Versionsverlauf", "Die komplette Versionsgeschichte eines Projekts. "
                  "Gehört zum Projekt – nicht separat löschen.", "keep", None, None, "code")

    # KI
    for base in _AI:
        if under(p, base):
            return _r("ai", "KI-Modelle", "Heruntergeladene KI-Modelle – oft mehrere GB groß, aber jederzeit "
                      "erneut herunterladbar. Löschen, wenn du das Modell nicht mehr nutzt.", "review", None, None, "cpu")
    if name in ("models", "checkpoints", "loras", "lora", "vae") and any(
            k in p for k in ("comfy", "stable-diffusion", "automatic1111", "invokeai", "fooocus", "forge")):
        return _r("ai", "KI-Modelle", "Bildgenerierungs-Modelle. Groß, aber neu herunterladbar.",
                  "review", None, None, "cpu")

    # Cloud & persönliche Ordner
    for od in ONEDRIVE:
        if under(p, od):
            return _r("cloud", "OneDrive-Ordner",
                      "Wird mit OneDrive synchronisiert – Löschen entfernt die Dateien auch in der Cloud! "
                      "Tipp: Rechtsklick › „Speicherplatz freigeben“ behält sie nur online.",
                      "review", None, "onedrive", "cloud")
    if under(p, KF.get("downloads", "")):
        return _r("download", "Download",
                  "Heruntergeladene Dateien. Installer und entpackte Archive braucht man danach meist nicht mehr.",
                  "likely" if age_days > 90 else "review", None, None, "download")
    if under(p, KF.get("savedgames", "")):
        return _r("saves", "Spielstände", "Gespeicherte Spielstände. Nur löschen, wenn du das Spiel nicht "
                  "mehr spielst.", "keep", None, None, "game")
    for key, label in (("desktop", "Desktop"), ("documents", "Dokumente"), ("pictures", "Bilder"),
                       ("videos", "Videos"), ("music", "Musik")):
        if under(p, KF.get(key, "")):
            return _r("personal", f"Persönliche Dateien ({label})",
                      "Deine eigenen Dateien. Prüfe den Inhalt – alternativ auf eine externe Festplatte "
                      "auslagern statt löschen.", "review", None, None, "user")

    # App-Daten
    for base, label in ((LOCAL, "Local"), (ROAMING, "Roaming"), (LOCALLOW, "LocalLow")):
        if under(p, base) and p != nc(base):
            vendor = first_component(path, base)
            if vendor.lower() in _SYSTEM_APPDATA or under(p, os.path.join(base, "Microsoft")):
                return _r("appdata", f"App-Daten „{vendor}“", "Daten von Windows oder Treibern.",
                          "keep", "Windows-/Treiberdaten", None, "shield")
            if age_days > 365 and not looks_installed(vendor):
                return _r("leftover", f"Überrest von „{vendor}“",
                          "Für diesen Ordner wurde kein installiertes Programm gefunden – vermutlich ein Überbleibsel "
                          "einer deinstallierten App. Seit über einem Jahr unverändert.", "likely", None, None, "box")
            return _r("appdata", f"App-Daten „{vendor}“",
                      "Einstellungen und Daten einer App. Löschen setzt die App zurück (z. B. Logins, Einstellungen).",
                      "review", None, None, "box")

    if any(k in name for k in ("backup", "sicherung", "bak")):
        return _r("backup", "Sicherung", "Ein Backup. Prüfe, ob es eine aktuellere Sicherung gibt, "
                  "bevor du es löschst.", "review", None, None, "archive")

    if age_days >= 730:
        return _r("old", "Lange nicht benutzt",
                  "Seit über zwei Jahren hat sich hier nichts verändert. Wahrscheinlich nicht mehr benötigt – "
                  "kurz reinschauen und dann löschen oder archivieren.", "likely", None, None, "clock")
    return _r("old", "Länger nicht benutzt",
              "Hier hat sich länger nichts getan. Prüfe den Inhalt, bevor du löschst.", "review", None, None, "clock")


def _after(path, marker):
    low = path.lower()
    i = low.find(marker)
    rest = path[i + len(marker):].lstrip("\\")
    return rest.split("\\", 1)[0] or path


def classify_file(path, age_days=0, size=0):
    p = nc(path)
    name = os.path.basename(p)
    ext = os.path.splitext(name)[1]
    parent = os.path.dirname(p)

    if parent.rstrip("\\") == nc(SYSDRIVE).rstrip("\\") or len(parent.rstrip("\\")) == 2:
        if name == "pagefile.sys":
            return _r("system", "Auslagerungsdatei", "Erweitert den Arbeitsspeicher. Windows braucht sie – "
                      "nicht löschen.", "keep", "Systemdatei", None, "shield")
        if name == "hiberfil.sys":
            return _r("system", "Ruhezustandsdatei",
                      "Speichert den Arbeitsspeicher für den Ruhezustand/Schnellstart. Wenn du den Ruhezustand "
                      "nicht nutzt: Eingabeaufforderung als Admin öffnen und „powercfg /h off“ eingeben – "
                      "dann verschwindet die Datei.", "keep", "Systemdatei", None, "shield")
        if name == "swapfile.sys":
            return _r("system", "Auslagerungsdatei (Apps)", "Wird von Windows für Store-Apps genutzt.",
                      "keep", "Systemdatei", None, "shield")
        if name == "dumpstack.log.tmp":
            return _r("system", "Systemdatei", "Wird von Windows verwaltet.", "keep", "Systemdatei", None, "shield")

    sysr = _system_rules(p, name)
    if sysr and sysr["level"] == "keep":
        return sysr
    gi = _game_info(path, is_file=True)
    if gi:
        return gi
    folder = classify_folder(os.path.dirname(path), age_days, size)
    if folder["kind"] == "game" and folder["level"] == "uninstall":
        folder = dict(folder)
        folder["title"] = "Datei aus " + folder["title"]
        folder["text"] = ("Gehört zu einem installierten Spiel. Einzelne Spieldateien zu löschen beschädigt das "
                          "Spiel – deinstalliere lieber das ganze Spiel über den Launcher, wenn du es nicht mehr spielst.")
        folder["protect"] = folder["protect"] or "Einzelne Spieldateien nicht löschen – ganzes Spiel deinstallieren"
        return folder
    if folder["protect"] or (folder["kind"] in ("cache", "temp", "dev") and folder["level"] == "safe") \
            or folder["kind"] == "game":
        folder = dict(folder)
        folder["title"] = folder["title"] + " – Datei"
        return folder

    in_downloads = under(p, KF.get("downloads", ""))
    old = age_days > 180

    if ext == ".dmp" or name == "memory.dmp":
        return _r("dump", "Absturzabbild", "Wird nach Programm- oder Systemabstürzen geschrieben. Nur für "
                  "Entwickler interessant – kann weg.", "safe", None, None, "alert")
    if ext in (".tmp", ".temp", ".bak", ".old", ".partial", ".crdownload", ".part"):
        return _r("temp", "Temporäre/alte Datei", "Zwischen- oder Sicherungsdatei, meist überflüssig.",
                  "likely", None, None, "sparkles")
    if ext == ".log":
        return _r("logs", "Riesige Logdatei", "Protokolldatei, die stark angewachsen ist. Kann gelöscht werden; "
                  "das Programm legt bei Bedarf eine neue an.", "likely", None, None, "doc")
    if ext in VM:
        if name == "ext4.vhdx":
            t = "Virtuelle Festplatte deines WSL-Linux. Nicht löschen, solange du WSL nutzt – sonst "
            t += "„wsl --unregister <Distribution>“ verwenden."
            return _r("vm", "WSL-Linux-Festplatte", t, "keep", None, None, "box")
        if "docker" in p:
            return _r("vm", "Docker-Daten", "Enthält alle Docker-Images und Container. In Docker Desktop über "
                      "„Clean / Purge data“ verkleinern statt löschen.", "review", None, None, "box")
        return _r("vm", "Virtuelle Festplatte", "Festplatte einer virtuellen Maschine. Nur löschen, wenn du die "
                  "VM nicht mehr brauchst.", "review", None, None, "box")
    if ext in INSTALLER:
        if in_downloads:
            return _r("installer", "Installationsprogramm", "Heruntergeladener Installer. Nach der Installation "
                      "nicht mehr nötig und jederzeit neu herunterladbar.", "likely", None, None, "download")
        return _r("installer", "Programmdatei", "Ausführbare Datei oder Installer.", "review", None, None, "package")
    if ext in IMAGE_DISK and ext != ".bin":
        return _r("disk", "Disk-Abbild (ISO/IMG)", "Abbild einer CD/DVD oder eines Installationsmediums. Meist "
                  "nur einmal zum Installieren gebraucht und neu herunterladbar.", "likely" if old or in_downloads
                  else "review", None, None, "disc")
    if ext in ARCHIVE:
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.lower().endswith(".tar"):
            stem = stem[:-4]
        sibling = os.path.join(os.path.dirname(path), stem)
        if os.path.isdir(sibling):
            return _r("archive", "Archiv – bereits entpackt",
                      f"Daneben liegt bereits der entpackte Ordner „{stem}“. Das Archiv ist damit doppelt "
                      "vorhanden und kann meist gelöscht werden.", "likely" if age_days > 14 else "review",
                      None, None, "archive")
        return _r("archive", "Archiv (ZIP/RAR/7z)", "Gepackte Dateien. Wenn du den Inhalt schon entpackt hast "
                  "oder nicht mehr brauchst, kann es weg.", "likely" if in_downloads and old else "review",
                  None, None, "archive")
    if ext in AI_MODEL and ext != ".bin" or (ext == ".bin" and any(k in p for k in ("model", "huggingface", "ollama"))):
        return _r("ai", "KI-Modell", "Gewichte eines KI-Modells. Groß, aber in der Regel erneut herunterladbar.",
                  "review", None, None, "cpu")
    if ext in CONSOLE:
        return _r("game", "Spiel-Abbild", "Abbild eines Konsolenspiels. Behalten, wenn du es noch spielst.",
                  "review", None, None, "game")
    if ext in VIDEO:
        return _r("video", "Video", "Videodatei – oft der größte Platzfresser. Nicht mehr benötigte Aufnahmen "
                  "löschen oder auf eine externe Festplatte/Cloud verschieben.", "likely" if in_downloads and old
                  else "review", None, None, "video")
    if ext in AUDIO:
        return _r("audio", "Audiodatei", "Musik oder Aufnahme in hoher Qualität.", "review", None, None, "music")
    if ext in PHOTO_RAW:
        return _r("photo", "Bild/Projektdatei", "Große Bild- oder Grafikdatei (RAW/PSD).", "review", None, None, "image")
    if ext in DOC_DB:
        return _r("mail", "Outlook-Postfach", "Lokale Kopie deiner E-Mails. Nicht löschen, solange Outlook sie "
                  "verwendet.", "keep", None, None, "doc")
    if ext in GAME_DATA:
        return _r("game", "Spieldaten", "Daten eines installierten Spiels. Spiel lieber komplett deinstallieren "
                  "als einzelne Dateien löschen.", "keep", None, None, "game")
    if ext == ".bin" and ".bin" in IMAGE_DISK:
        return _r("disk", "Binärdatei/Abbild", "Rohdaten oder Disk-Abbild. Prüfe, wozu sie gehört.",
                  "review", None, None, "disc")
    return _r("file", "Große Datei", "Prüfe, ob du diese Datei noch brauchst.",
              "likely" if age_days > 730 else "review", None, None, "file")


_LEVEL_SCORE = {"safe": 90, "likely": 70, "uninstall": 50, "review": 35, "keep": 5}


def score(level, age_days, size):
    import math
    s = _LEVEL_SCORE.get(level, 30)
    s += min(20, age_days / 365 * 7)
    s += min(20, max(0, math.log2(max(size, 1) / (100 * 1024 * 1024)) * 4))
    return round(s, 1)
