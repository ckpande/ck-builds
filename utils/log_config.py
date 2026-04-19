# log_config.py
# Chandrakant Pande - ckpande

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name, path, level=logging.INFO, max_size=2 * 1024 * 1024, backups=3, console=True):
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(level)
    log.propagate = False
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    fh = RotatingFileHandler(path, maxBytes=max_size, backupCount=backups)
    fh.setFormatter(fmt)
    log.addHandler(fh)
    if console:
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        log.addHandler(ch)
    return log


if __name__ == "__main__":
    import tempfile

    p = os.path.join(tempfile.gettempdir(), "test.log")
    l = setup_logger("t", p, console=True)
    l.info("test log entry")
    l2 = setup_logger("t", p)
    print(f"Log file: {p}")
    print("ok" if l is l2 else "fail")
