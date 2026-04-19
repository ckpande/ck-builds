# thread_pool.py
# Chandrakant Pande - ckpande

from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError


def run_parallel(func, items, workers=4, timeout=None):
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(func, i): i for i in items}
        for f in as_completed(futures, timeout=timeout):
            i = futures[f]
            try:
                results.append({"item": i, "result": f.result(), "error": None})
            except TimeoutError as e:
                results.append({"item": i, "result": None, "error": e})
            except Exception as e:
                results.append({"item": i, "result": None, "error": e})
    return results


if __name__ == "__main__":
    def square(x):
        return x * x


    print(run_parallel(square, [1, 2, 3, 4, 5], workers=3))
