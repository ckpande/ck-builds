# singleton.py
# Chandrakant Pande - ckpande

import threading
import functools


def singleton(cls):
    instance = None
    lock = threading.Lock()

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal instance
        if instance is None:
            with lock:
                if instance is None:
                    instance = cls(*args, **kwargs)
        return instance

    return wrapper


if __name__ == "__main__":
    @singleton
    class Config:
        def __init__(self):
            self.data = {}


    c1 = Config()
    c2 = Config()
    print(c1 is c2)
    print(Config.__name__)
