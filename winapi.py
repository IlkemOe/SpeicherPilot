"""Kleine ctypes-Hilfen für Windows: Laufwerke, bekannte Ordner, Papierkorb, Adminrechte."""
import ctypes
import os
import shutil
import string
import uuid
import winreg
from ctypes import wintypes

shell32 = ctypes.windll.shell32
kernel32 = ctypes.windll.kernel32
ole32 = ctypes.windll.ole32


def is_admin():
    try:
        return bool(shell32.IsUserAnAdmin())
    except Exception:
        return False


# --------------------------------------------------------------- bekannte Ordner
class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

    def __init__(self, text):
        super().__init__()
        u = uuid.UUID(text)
        self.Data1, self.Data2, self.Data3 = u.fields[0], u.fields[1], u.fields[2]
        for i, b in enumerate(u.bytes[8:]):
            self.Data4[i] = b


_FOLDER_IDS = {
    "desktop": "B4BFCC3A-DB2C-424C-B029-7FE99A87C641",
    "documents": "FDD39AD0-238F-46AF-ADB4-6C85480369C7",
    "downloads": "374DE290-123F-4565-9164-39C4925E467B",
    "pictures": "33E28130-4E1E-4676-835A-98395C3BC3BB",
    "videos": "18989B1D-99B5-455B-841C-AB7C74E4DDFC",
    "music": "4BD8D571-6D19-48D3-BE97-422220080E43",
    "savedgames": "4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4",
}


def known_folder(guid_text):
    ptr = ctypes.c_wchar_p()
    try:
        hr = shell32.SHGetKnownFolderPath(ctypes.byref(GUID(guid_text)), 0, None, ctypes.byref(ptr))
    except Exception:
        return None
    if hr != 0:
        return None
    value = ptr.value
    ole32.CoTaskMemFree(ptr)
    return value


def known_folders():
    home = os.path.expanduser("~")
    fallback = {"desktop": "Desktop", "documents": "Documents", "downloads": "Downloads",
                "pictures": "Pictures", "videos": "Videos", "music": "Music",
                "savedgames": "Saved Games"}
    out = {}
    for key, guid in _FOLDER_IDS.items():
        out[key] = known_folder(guid) or os.path.join(home, fallback[key])
    return out


# --------------------------------------------------------------- Laufwerke
def drives():
    result = []
    mask = kernel32.GetLogicalDrives()
    system_drive = os.environ.get("SystemDrive", "C:").upper()
    for i, letter in enumerate(string.ascii_uppercase):
        if not mask & (1 << i):
            continue
        root = f"{letter}:\\"
        dtype = kernel32.GetDriveTypeW(root)
        if dtype not in (2, 3):  # 2 = Wechseldatenträger, 3 = Festplatte
            continue
        try:
            total, used, free = shutil.disk_usage(root)
        except OSError:
            continue
        label_buf = ctypes.create_unicode_buffer(261)
        fs_buf = ctypes.create_unicode_buffer(261)
        kernel32.GetVolumeInformationW(root, label_buf, 261, None, None, None, fs_buf, 261)
        result.append({
            "root": root,
            "letter": letter,
            "label": label_buf.value or ("Lokaler Datenträger" if dtype == 3 else "Wechseldatenträger"),
            "fs": fs_buf.value,
            "type": "fixed" if dtype == 3 else "removable",
            "system": f"{letter}:" == system_drive,
            "total": total,
            "used": used,
            "free": free,
        })
    return result


# --------------------------------------------------------------- Papierkorb
class SHQUERYRBINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("i64Size", ctypes.c_longlong),
                ("i64NumItems", ctypes.c_longlong)]


def recycle_bin_info():
    info = SHQUERYRBINFO()
    info.cbSize = ctypes.sizeof(info)
    try:
        hr = shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
    except Exception:
        return {"size": 0, "items": 0}
    if hr != 0:
        return {"size": 0, "items": 0}
    return {"size": int(info.i64Size), "items": int(info.i64NumItems)}


def empty_recycle_bin():
    # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    shell32.SHEmptyRecycleBinW(None, None, 0x1 | 0x2 | 0x4)
    return recycle_bin_info()["items"] == 0


def _parse_info_file(data):
    """$I-Datei des Papierkorbs lesen -> (Originalgröße, Löschzeit (Unix), Originalpfad)."""
    ver = int.from_bytes(data[0:8], "little")
    size = int.from_bytes(data[8:16], "little")
    ft = int.from_bytes(data[16:24], "little")
    if ver >= 2:
        n = int.from_bytes(data[24:28], "little")
        path = data[28:28 + 2 * n].decode("utf-16-le", "replace")
    else:
        path = data[24:24 + 520].decode("utf-16-le", "replace")
    path = path.split("\0", 1)[0]
    deleted = ft / 1e7 - 11644473600 if ft else 0
    return size, deleted, path


def recycle_bin_items():
    """Alle Einträge im Papierkorb des aktuellen Benutzers (alle Laufwerke)."""
    out = []
    for d in drives():
        rb = os.path.join(d["root"], "$Recycle.Bin")
        try:
            sids = [e.path for e in os.scandir(rb) if e.is_dir(follow_symlinks=False)]
        except OSError:
            continue
        for sid in sids:
            try:
                entries = list(os.scandir(sid))
            except OSError:
                continue  # Papierkorb anderer Benutzer
            for e in entries:
                if not e.name.startswith("$I"):
                    continue
                rpath = os.path.join(sid, "$R" + e.name[2:])
                if not os.path.exists(rpath):
                    continue
                try:
                    with open(e.path, "rb") as f:
                        size, deleted, orig = _parse_info_file(f.read())
                except OSError:
                    continue
                out.append({"path": rpath, "name": os.path.basename(orig) or orig, "orig": orig,
                            "size": size, "mtime": deleted, "deleted": deleted,
                            "isDir": os.path.isdir(rpath)})
    out.sort(key=lambda x: -x["size"])
    return out


def _info_path(rpath):
    d, b = os.path.split(rpath)
    return os.path.join(d, "$I" + b[2:])


def _is_bin_entry(rpath):
    parts = os.path.normpath(rpath).split("\\")
    return len(parts) == 4 and parts[1].lower() == "$recycle.bin" and parts[3].startswith("$R")


def recycle_bin_delete(rpath):
    """Einen Papierkorb-Eintrag endgültig löschen."""
    if not _is_bin_entry(rpath):
        return False
    import stat as _stat

    def onexc(func, p, exc):
        try:
            os.chmod(p, _stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    try:
        if os.path.isdir(rpath):
            shutil.rmtree(rpath, onexc=onexc)
        elif os.path.exists(rpath):
            os.remove(rpath)
        if not os.path.exists(rpath) and os.path.exists(_info_path(rpath)):
            os.remove(_info_path(rpath))
    except OSError:
        return False
    return not os.path.exists(rpath)


def recycle_bin_restore(rpath):
    """Eintrag an den ursprünglichen Ort zurücklegen. Gibt (ok, Fehlertext) zurück."""
    if not _is_bin_entry(rpath) or not os.path.exists(rpath):
        return False, "Eintrag nicht gefunden"
    try:
        with open(_info_path(rpath), "rb") as f:
            _, _, orig = _parse_info_file(f.read())
    except OSError:
        return False, "Ursprungsort unbekannt"
    if os.path.exists(orig):
        return False, "Am ursprünglichen Ort existiert bereits eine Datei mit diesem Namen"
    try:
        os.makedirs(os.path.dirname(orig), exist_ok=True)
        shutil.move(rpath, orig)
        os.remove(_info_path(rpath))
    except OSError as exc:
        return False, str(exc)
    return True, orig


class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT),
                ("pFrom", ctypes.c_void_p), ("pTo", ctypes.c_void_p),
                ("fFlags", ctypes.c_uint16), ("fAnyOperationsAborted", wintypes.BOOL),
                ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", ctypes.c_void_p)]


FO_DELETE = 3
FOF_SILENT = 0x4
FOF_NOCONFIRMATION = 0x10
FOF_ALLOWUNDO = 0x40
FOF_NOERRORUI = 0x400


def move_to_recycle_bin(path):
    """Verschiebt Datei/Ordner (oder eine Liste davon) in den Papierkorb. True bei Erfolg."""
    paths = [path] if isinstance(path, str) else list(path)
    if not paths:
        return True
    joined = "\0".join(os.path.abspath(p) for p in paths)
    buf = ctypes.create_unicode_buffer(joined, len(joined) + 2)  # doppelt nullterminiert
    op = SHFILEOPSTRUCTW()
    op.wFunc = FO_DELETE
    op.pFrom = ctypes.cast(buf, ctypes.c_void_p)
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_NOERRORUI | FOF_SILENT
    rc = shell32.SHFileOperationW(ctypes.byref(op))
    return rc == 0 and not op.fAnyOperationsAborted


# --------------------------------------------------------------- Neustart als Admin
def relaunch_as_admin(script, args=""):
    import sys
    params = f'"{script}" {args}'.strip()
    exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(exe):
        exe = sys.executable
    rc = shell32.ShellExecuteW(None, "runas", exe, params, os.path.dirname(script), 1)
    return rc > 32


# --------------------------------------------------------------- installierte Programme
def installed_programs():
    """Liefert eine Menge normalisierter Namen/Hersteller/Ordner installierter Programme."""
    names = set()
    keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, sub in keys:
        try:
            root = winreg.OpenKey(hive, sub)
        except OSError:
            continue
        with root:
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(root, i)
                except OSError:
                    break
                i += 1
                try:
                    with winreg.OpenKey(root, name) as k:
                        for field in ("DisplayName", "Publisher", "InstallLocation"):
                            try:
                                v, _ = winreg.QueryValueEx(k, field)
                            except OSError:
                                continue
                            if isinstance(v, str) and v.strip():
                                if field == "InstallLocation":
                                    v = os.path.basename(v.rstrip("\\/"))
                                names.add(v)
                except OSError:
                    continue
    return names
