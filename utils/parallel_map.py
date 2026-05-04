# parallel_map.py
# Chandrakant Pande - ckpande

import time
from concurrent.futures import ProcessPoolExecutor


def heavy(x):
    total = 0
    for i in range(5_000_000):
        total += i * x
    return total


def parallel_map(func, items, workers=None, chunksize=1):
    items = list(items)
    if not items:
        return []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(func, items, chunksize=chunksize))


if __name__ == "__main__":
    data = [1, 2, 3, 4, 5, 6, 7, 8]

    start = time.time()
    seq = [heavy(x) for x in data]
    print(f"sequential: {time.time() - start:.2f}s")

    start = time.time()
    par = parallel_map(heavy, data)
    print(f"parallel:   {time.time() - start:.2f}s")

    assert seq == par
