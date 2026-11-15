"""Schneller, speichersparender Verzeichnis-Scan mit Aggregation pro Ordner."""
import heapq
import os
import shutil
import threading
import time

import knowledge

ATTR_DIR = 0x10
ATTR_REPARSE = 0x400
ATTR_CLOUD = 0x1000 | 0x40000 | 0x400000  # offline / recall on open / recall on data access
TAG_SYMLINK = 0xA000000C
TAG_MOUNT = 0xA0000003
LARGE_MIN = 50 * 1024 * 1024
LARGE_KEEP = 800


class Node:
    __slots__ = ("path", "name", "parent", "children", "size", "own", "files", "dirs",
                 "mtime", "atime", "denied", "kind")

    def __init__(self, path, name, parent, kind="dir"):
        self.path = path
        self.name = name
        self.parent = parent
        self.children = []
        self.size = 0
        self.own = 0
        self.files = 0
        self.dirs = 0
        self.mtime = 0.0
        self.atime = 0.0
        self.denied = False
        self.kind = kind


def _is_drive_root(p):
    drive, rest = os.path.splitdrive(p)
    return bool(drive) and rest in ("", "\\", "/")


def normalize_roots(roots):
    """Absolute Pfade, Duplikate und verschachtelte Wurzeln entfernen."""
    clean = []
    for r in roots:
        if not r:
            continue
        r = os.path.abspath(r)
        if _is_drive_root(r):
            r = os.path.splitdrive(r)[0] + "\\"
        if os.path.isdir(r):
            clean.append(r)
    clean.sort(key=lambda x: len(x))
    out = []
    for r in clean:
        n = knowledge.nc(r)
        if any(knowledge.under(n, o) for o in out):
            continue
        out.append(r)
    return out


class Scanner:
    def __init__(self, skip_paths):
        self.lock = threading.RLock()
        self.skip = {knowledge.nc(p) for p in skip_paths if p}
        self.state = "idle"
        self.root = None
        self.index = {}
        self.large = []
        self.roots = []
        self.finished_at = None
        self.on_done = None
        self._cancel = False
        self._reset_progress()

    def _reset_progress(self):
        self.files = 0
        self.dirs = 0
        self.bytes = 0
        self.cloud = 0
        self.current = ""
        self.started = time.time()
        self.expected = 0
        self.error = None

    # ------------------------------------------------------------ Steuerung
    def start(self, roots):
        if self.state == "scanning":
            return False, "Es läuft bereits eine Analyse."
        roots = normalize_roots(roots)
        if not roots:
            return False, "Keine gültigen Ordner ausgewählt."
        self._cancel = False
        self._reset_progress()
        expected = 0
        for r in roots:
            if _is_drive_root(r):
                try:
                    expected += shutil.disk_usage(r).used
                except OSError:
                    pass
        self.expected = expected
        self.state = "scanning"
        self.roots = roots
        threading.Thread(target=self._run, args=(roots,), daemon=True).start()
        return True, None

    def cancel(self):
        self._cancel = True

    def status(self):
        return {
            "state": self.state,
            "files": self.files,
            "dirs": self.dirs,
            "bytes": self.bytes,
            "cloud": self.cloud,
            "current": self.current,
            "elapsed": round(time.time() - self.started, 1),
            "expected": self.expected,
            "roots": self.roots,
            "finishedAt": self.finished_at,
            "error": self.error,
        }

    # ------------------------------------------------------------ Scan
    def _run(self, roots):
        try:
            root = Node("", "Dieser PC", None, "virtual")
            all_nodes = []
            heap = []
            for r in roots:
                is_drive = _is_drive_root(r)
                name = r if is_drive else (os.path.basename(r.rstrip("\\")) or r)
                top = Node(r, name, root, "drive" if is_drive else "dir")
                root.children.append(top)
                self._walk(top, all_nodes, heap)
                if self._cancel:
                    break
            if self._cancel:
                self.state = "cancelled"
                return

            for n in all_nodes:
                n.size = n.own
            for n in reversed(all_nodes):
                p = n.parent
                if p is None:
                    continue
                p.size += n.size
                p.files += n.files
                p.dirs += n.dirs + 1
                if n.mtime > p.mtime:
                    p.mtime = n.mtime
                if n.atime > p.atime:
                    p.atime = n.atime

            # Nicht erfasster Rest (Windows, geschützte Bereiche, Systemdateien)
            for top in root.children:
                if top.kind != "drive":
                    continue
                try:
                    used = shutil.disk_usage(top.path).used
                except OSError:
                    continue
                rest = used - top.size
                if rest > max(used * 0.005, 256 * 1024 * 1024):
                    sysn = Node(top.path + "::system", "System & geschützte Bereiche", top, "system")
                    sysn.size = rest
                    top.children.append(sysn)
                    top.size += rest
                    root.size += rest

            index = {"": root}
            for n in all_nodes:
                index[knowledge.nc(n.path)] = n
            now = time.time()
            large = sorted(heap, reverse=True)
            large = [{"path": p, "size": s, "mtime": m, "atime": min(a, now)} for s, p, m, a in large]
            with self.lock:
                self.root = root
                self.index = index
                self.large = large
            self.finished_at = time.time()
            if self.on_done:  # z. B. Spiele neu zuordnen, bevor Ergebnisse abgefragt werden
                try:
                    self.current = "Spiele werden zugeordnet …"
                    self.on_done()
                except Exception:
                    pass
            self.state = "done"
        except Exception as exc:  # pragma: no cover - Sicherheitsnetz
            import traceback
            traceback.print_exc()
            self.error = str(exc)
            self.state = "error"

    def _walk(self, top, all_nodes, heap):
        stack = [top]
        all_nodes.append(top)
        skip = self.skip
        nc = knowledge.nc
        now = time.time()
        while stack:
            if self._cancel:
                return
            node = stack.pop()
            try:
                it = os.scandir(node.path)
            except OSError:
                node.denied = True
                continue
            try:
                with it:
                    for e in it:
                        try:
                            st = e.stat(follow_symlinks=False)
                        except OSError:
                            continue
                        a = st.st_file_attributes
                        if a & ATTR_DIR:
                            if a & ATTR_REPARSE:
                                tag = getattr(st, "st_reparse_tag", 0)
                                if tag in (TAG_SYMLINK, TAG_MOUNT) or e.is_symlink() or \
                                        getattr(e, "is_junction", lambda: False)():
                                    continue
                            if skip and nc(e.path) in skip:
                                continue
                            c = Node(e.path, e.name, node)
                            c.mtime = st.st_mtime
                            node.children.append(c)
                            all_nodes.append(c)
                            stack.append(c)
                        else:
                            if a & ATTR_CLOUD:
                                self.cloud += st.st_size
                                sz = 0
                            else:
                                sz = st.st_size
                            node.own += sz
                            node.files += 1
                            m = st.st_mtime
                            at = st.st_atime
                            if at > now:
                                at = m
                            if m > node.mtime:
                                node.mtime = m
                            if at > node.atime:
                                node.atime = at
                            if sz >= LARGE_MIN:
                                item = (sz, e.path, m, at)
                                if len(heap) < LARGE_KEEP:
                                    heapq.heappush(heap, item)
                                elif sz > heap[0][0]:
                                    heapq.heapreplace(heap, item)
                            self.files += 1
                            self.bytes += sz
            except OSError:
                node.denied = True
            self.dirs += 1
            if self.dirs % 64 == 0:
                self.current = node.path

    # ------------------------------------------------------------ Abfragen
    def get(self, path):
        return self.index.get(knowledge.nc(path) if path else "")

    def in_scope(self, path):
        p = knowledge.nc(path)
        return any(knowledge.under(p, r) for r in self.roots) and self.root is not None

    def unused(self, days, minsize, basis):
        with self.lock:
            if not self.root:
                return []
            now = time.time()
            out = []
            stack = list(self.root.children)
            while stack:
                n = stack.pop()
                if n.kind == "system" or n.size < minsize:
                    continue
                t = n.mtime if basis == "modified" else max(n.mtime, n.atime)
                age = (now - t) / 86400 if t else 99999
                if n.kind == "dir" and age >= days and not knowledge.is_container(n.path):
                    out.append((n, age))
                    continue
                stack.extend(n.children)
            return out

    def remove_path(self, path, freed, gone):
        """Baum nach dem Löschen aktualisieren."""
        with self.lock:
            p = knowledge.nc(path)
            node = self.index.get(p)
            if node is not None:
                parent = node.parent
                if gone:
                    if parent is not None and node in parent.children:
                        parent.children.remove(node)
                    stack = [node]
                    while stack:
                        x = stack.pop()
                        self.index.pop(knowledge.nc(x.path), None)
                        stack.extend(x.children)
                    sub_files = node.files
                else:
                    node.size = max(0, node.size - freed)
                    sub_files = 0
                    parent = node.parent
                x = parent
                while x is not None:
                    x.size = max(0, x.size - freed)
                    x.files = max(0, x.files - sub_files)
                    x = x.parent
                self.large = [f for f in self.large if not knowledge.under(knowledge.nc(f["path"]), p)]
                return
            # Einzelne Datei
            parent = self.index.get(knowledge.nc(os.path.dirname(path)))
            if gone:
                self.large = [f for f in self.large if knowledge.nc(f["path"]) != p]
            if parent is not None:
                parent.own = max(0, parent.own - freed)
                x = parent
                while x is not None:
                    x.size = max(0, x.size - freed)
                    if gone:
                        x.files = max(0, x.files - 1)
                    x = x.parent
