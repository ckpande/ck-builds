# timer.py
# Chandrakant Pande - ckpande

import time


class Timer:
    def __init__(self, label=None):
        self.label = label
        self.start = None
        self.end = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, ex_type, ex_val, ex_tb):
        self.end = time.perf_counter()
        msg = f"{self.label}: " if self.label else ""
        print(f"[Timer] {msg}{self.delta:.4f}s")
        return False

    @property
    def delta(self):
        if self.start is not None and self.end is not None:
            return self.end - self.start
        return 0.0


if __name__ == "__main__":
    with Timer("sleep"):
        time.sleep(0.1)
        
    with Timer():
        sum(range(1_000_000))
