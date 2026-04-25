# background_task.py
# Chandrakant Pande - ckpande

import threading
import logging
from functools import wraps

log = logging.getLogger("background_tasks")


def background_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        def run():
            try:
                func(*args, **kwargs)
            except Exception:
                log.exception("Background task '%s' failed", func.__name__)

        thread_name = f"bg-{func.__name__}"
        thread = threading.Thread(target=run, name=thread_name)
        thread.daemon = True
        thread.start()

    return wrapper


if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


    @background_task
    def long_task(name):
        time.sleep(1)
        if name == "B":
            raise ValueError("Simulated crash")
        print(f"Task {name} done")


    print("Calling tasks...")
    long_task("A")
    long_task("B")
    print("Main continues immediately")
    time.sleep(1.5)
