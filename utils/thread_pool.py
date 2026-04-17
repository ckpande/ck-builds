# thread_pool.py
# Chandrakant Pande - ckpande

from concurrent.futures import ThreadPoolExecutor, as_completed


def run_parallel(func, items, workers=4):
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(func, item): item for item in items}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(e)
    return results


if __name__ == "__main__":
    def square(x):
        return x * x


    print(run_parallel(square, [1, 2, 3, 4, 5], workers=3))
