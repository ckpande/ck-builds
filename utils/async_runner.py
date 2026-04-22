# async_runner.py
# Chandrakant Pande - ckpande

import asyncio
import atexit
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

_executor = ThreadPoolExecutor()
atexit.register(_executor.shutdown, wait=True)


async def run_sync(func: Callable, *args: Any, **kwargs: Any) -> Any:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))


async def gather_sync(func: Callable, items: list) -> list:
    tasks = [run_sync(func, i) for i in items]
    return await asyncio.gather(*tasks)


def run_async_from_sync(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


def run_sync_simple(func: Callable, *args: Any, **kwargs: Any) -> Any:
    return _executor.submit(func, *args, **kwargs).result()


if __name__ == "__main__":
    import time


    def blocking(x: int) -> int:
        time.sleep(0.2)
        return x * 2


    async def demo() -> None:
        print(await run_sync(blocking, 5))
        results = await gather_sync(blocking, [1, 2, 3])
        print(results)


    asyncio.run(demo())
    print(run_sync_simple(blocking, 10))
    print(run_async_from_sync(asyncio.sleep(0.1, result="ok")))
