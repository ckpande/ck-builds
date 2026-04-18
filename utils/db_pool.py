# db_pool.py
# Chandrakant Pande - ckpande

import threading
from queue import Queue


class DBPool:
    def __init__(self, creator, max_size=5):
        self.creator = creator
        self.max_size = max_size
        self._pool = Queue(maxsize=max_size)
        self._size = 0
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            if not self._pool.empty():
                return self._pool.get()
            if self._size < self.max_size:
                self._size += 1
                return self.creator()
        return self._pool.get()

    def put(self, conn):
        self._pool.put(conn)


if __name__ == "__main__":
    def create_stub():
        return {"conn": "stub"}


    pool = DBPool(create_stub, max_size=2)
    c1 = pool.get()
    c2 = pool.get()
    pool.put(c1)
    c3 = pool.get()
    print(c1, c2, c3)
