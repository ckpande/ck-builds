# object_pool.py
# Chandrakant Pande - ckpande

class ObjectPool:
    def __init__(self, creator, max_size=5):
        self.creator = creator
        self.max_size = max_size
        self._pool = []
        self._in_use = []

    def acquire(self):
        if self._pool:
            obj = self._pool.pop()
            self._in_use.append(obj)
            return obj
        if len(self._in_use) < self.max_size:
            obj = self.creator()
            self._in_use.append(obj)
            return obj
        raise RuntimeError("Pool exhausted")

    def release(self, obj):
        for i, o in enumerate(self._in_use):
            if o is obj:
                del self._in_use[i]
                self._pool.append(obj)
                return
        raise ValueError("Object not from this pool")

    @property
    def stats(self):
        return {
            "available": len(self._pool),
            "in_use": len(self._in_use),
            "max_size": self.max_size,
        }

    def __repr__(self):
        s = self.stats
        return f"ObjectPool(available={s['available']}, in_use={s['in_use']}, max={s['max_size']})"


if __name__ == "__main__":
    def make_conn():
        return {"conn": "stub"}


    pool = ObjectPool(make_conn, max_size=2)
    c1 = pool.acquire()
    c2 = pool.acquire()
    pool.release(c1)
    c3 = pool.acquire()
    print(c1, c2, c3)
    print(c3 is c1)
