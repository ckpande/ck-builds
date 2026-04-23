# circuit_breaker.py
# Chandrakant Pande - ckpande

import time
import threading
import logging
from functools import wraps

log = logging.getLogger("circuit_breaker")

_CLOSED = "CLOSED"
_OPEN = "OPEN"
_HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, name, fail_limit=5, reset_timeout=60):
        self.name = name
        self.fail_limit = fail_limit
        self.reset_timeout = reset_timeout
        self._fail_count = 0
        self._state = _CLOSED
        self._last_fail_time = 0
        self._lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self._lock:
            if self._state == _OPEN:
                if time.time() - self._last_fail_time > self.reset_timeout:
                    self._state = _HALF_OPEN
                    log.info("circuit '%s' -> HALF_OPEN", self.name)
                else:
                    raise CircuitBreakerOpenError(f"circuit '{self.name}' OPEN")

        try:
            result = func(*args, **kwargs)
            with self._lock:
                if self._state == _HALF_OPEN:
                    self._state = _CLOSED
                    self._fail_count = 0
                    log.info("circuit '%s' -> CLOSED (recovered)", self.name)
            return result
        except Exception:
            with self._lock:
                self._fail_count += 1
                self._last_fail_time = time.time()
                if self._state == _CLOSED and self._fail_count >= self.fail_limit:
                    self._state = _OPEN
                    log.warning("circuit '%s' -> OPEN after %d fails", self.name, self._fail_count)
                elif self._state == _HALF_OPEN:
                    self._state = _OPEN
                    log.warning("circuit '%s' -> OPEN (probe fail)", self.name)
            raise


def circuit_breaker(name=None, fail_limit=5, reset_timeout=60):
    def decorator(func):
        cb = CircuitBreaker(name or func.__name__, fail_limit, reset_timeout)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    import random


    @circuit_breaker(fail_limit=2, reset_timeout=3)
    def unstable_api():
        if random.random() < 0.7:
            raise ValueError("API call failed")
        return "Success"


    for i in range(10):
        try:
            print(f"Call {i + 1}: {unstable_api()}")
        except Exception as e:
            print(f"Call {i + 1}: {e}")

        time.sleep(0.5)
