# log_config.py
# Chandrakant Pande - ckpande

import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, path, level=logging.INFO, max_size=2 * 1024 * 1024, backups=3):
    log = logging.getLogger(name)
    log.setLevel(level)
    h = RotatingFileHandler(path, maxBytes=max_size, backupCount=backups)
    fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    h.setFormatter(fmt)
    log.addHandler(h)
    return log


if __name__ == "__main__":
    l = setup_logger("test", "test.log")
    l.info("test log entry")
    print("done")
