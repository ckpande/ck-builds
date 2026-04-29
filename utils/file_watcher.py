# file_watcher.py
# Chandrakant Pande - ckpande

import os
import time


def file_snapshot(path):
    try:
        stat = os.stat(path)
        return (stat.st_mtime, stat.st_size)
    except (IOError, OSError):
        return None


class FileWatcher:
    def __init__(self, path, poll_interval=1.0):
        self.path = path
        self.interval = poll_interval
        self._snapshots = {}

    def scan(self):
        current = {}
        if os.path.isfile(self.path):
            current[self.path] = file_snapshot(self.path)
        elif os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for f in files:
                    full = os.path.join(root, f)
                    current[full] = file_snapshot(full)
        return current

    def check(self):
        new = self.scan()
        changes = []
        for f, snap in new.items():
            old = self._snapshots.get(f)
            if old is None:
                changes.append(("added", f))
            elif old != snap:
                changes.append(("modified", f))
        for f in self._snapshots:
            if f not in new:
                changes.append(("removed", f))
        self._snapshots = new
        return changes

    def watch(self, callback):
        self._snapshots = self.scan()
        while True:
            time.sleep(self.interval)
            for change in self.check():
                callback(*change)


if __name__ == "__main__":
    def on_change(typ, path):
        print(f"[{typ}] {path}")


    w = FileWatcher(".", poll_interval=2)
    print("Watching current directory... (Ctrl+C to stop)")
    try:
        w.watch(on_change)
    except KeyboardInterrupt:
        print("Stopped")
