# retry.py
# Chandrakant Pande - ckpande

import time
from functools import wraps


def retry(attempts=3, delay=1.0, backoff=2.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == attempts - 1:
                        raise
                    time.sleep(_delay)
                    _delay *= backoff

        return wrapper

    return decorator


if __name__ == "__main__":
    @retry(attempts=3, delay=0.5)
    def unstable():
        import random
        if random.random() < 0.7:
            raise ValueError("random fail")
        return "ok"


    unstable()
