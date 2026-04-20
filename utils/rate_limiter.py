# rate_limiter.py
# Chandrakant Pande - ckpande

import time
import threading
from contextlib import contextmanager


class RateLimiter:
    def __init__(self, max_calls: int, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self._calls = []
        self._lock = threading.Lock()

    def acquire(self) -> bool:
        with self._lock:
            now = time.time()
            self._calls = [t for t in self._calls if now - t < self.period]
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False

    def wait_and_acquire(self) -> None:
        while not self.acquire():
            time.sleep(0.05)

    @contextmanager
    def limited(self):
        if not self.acquire():
            raise RuntimeError(f"Rate limit: {self.max_calls} per {self.period}s")
        yield

    def stats(self) -> dict:
        with self._lock:
            now = time.time()
            active = [t for t in self._calls if now - t < self.period]
            return {
                "max_calls": self.max_calls,
                "period": self.period,
                "current_calls": len(active),
                "remaining": max(0, self.max_calls - len(active)),
            }

    def __repr__(self) -> str:
        s = self.stats()
        return f"RateLimiter(max={s['max_calls']}, period={s['period']}s, current={s['current_calls']}, remaining={s['remaining']})"


if __name__ == "__main__":
    limiter = RateLimiter(5, 1.0)
    for i in range(10):
        if limiter.acquire():
            print(f"call {i + 1} allowed")
        else:
            print(f"call {i + 1} blocked")
        time.sleep(0.1)

    print(limiter)
    with RateLimiter(2, 0.5).limited():
        print("within limit")
