# Chandrakant Pande - ckpande
import time
import threading
from functools import wraps

_MISSING = object()


class Cache:
    def __init__(self, ttl=60, maxsize=1000):
        self.ttl = ttl
        self.maxsize = maxsize
        self._data = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key):
        with self._lock:
            entry = self._data.get(key, _MISSING)
            if entry is _MISSING:
                self._misses += 1
                return _MISSING
            value, expiry = entry
            if time.time() > expiry:
                del self._data[key]
                self._misses += 1
                return _MISSING
            self._hits += 1
            return value

    def set(self, key, value):
        with self._lock:
            if key not in self._data and len(self._data) >= self.maxsize:
                oldest = next(iter(self._data))
                del self._data[oldest]
            self._data[key] = (value, time.time() + self.ttl)

    def delete(self, key):
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False

    def clear(self):
        with self._lock:
            self._data.clear()

    def cleanup(self):
        with self._lock:
            now = time.time()
            expired = [k for k, (_, exp) in self._data.items() if now > exp]
            for k in expired:
                del self._data[k]
            return len(expired)

    def stats(self):
        with self._lock:
            now = time.time()
            alive = sum(1 for _, exp in self._data.values() if now <= exp)
            total = self._hits + self._misses
            return {
                "size": len(self._data),
                "alive": alive,
                "expired": len(self._data) - alive,
                "maxsize": self.maxsize,
                "ttl": self.ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total, 3) if total else 0.0,
            }

    def __repr__(self):
        s = self.stats()
        return f"Cache(ttl={s['ttl']}s, size={s['size']}/{s['maxsize']}, hits={s['hits']}, misses={s['misses']}, hit_rate={s['hit_rate']})"


def cached(ttl=60, maxsize=1000):
    def decorator(func):
        _cache = Cache(ttl, maxsize)

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = repr((args, tuple(sorted(kwargs.items()))))
            result = _cache.get(key)
            if result is not _MISSING:
                return result
            result = func(*args, **kwargs)
            _cache.set(key, result)
            return result

        wrapper.cache = _cache
        return wrapper

    return decorator


if __name__ == "__main__":
    print("---< TTL expiry >---")
    c = Cache(ttl=1)
    c.set("a", 1)
    print(c.get("a"))
    time.sleep(1.1)
    print(c.get("a"))

    print("\n---< delete >---")
    c2 = Cache()
    c2.set("x", 10)
    c2.set("y", 20)
    c2.delete("x")
    print(c2.get("x"), c2.get("y"))

    print("\n---< cached decorator >---")


    @cached(ttl=2)
    def slow(x):
        time.sleep(0.2)
        return x * x


    t0 = time.perf_counter()
    print(slow(5))
    t1 = time.perf_counter()
    print(slow(5))
    t2 = time.perf_counter()
    print(f"first: {t1 - t0:.3f}s, second: {t2 - t1:.4f}s")

    print("\n---< cleanup and stats >---")
    c3 = Cache(ttl=1)
    c3.set("a", 1)
    c3.set("b", 2)
    time.sleep(1.1)
    print(f"before cleanup: {c3.stats()['size']} entries")
    c3.cleanup()
    print(f"after cleanup: {c3.stats()['size']} entries")

    print("\n---< None handling >---")
    cnt = [0]


    @cached(ttl=60)
    def maybe_none():
        cnt[0] += 1
        return None


    maybe_none()
    maybe_none()
    print(f"called {cnt[0]} times (should be 1)")
