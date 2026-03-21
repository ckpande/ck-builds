import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

DB_USER   = os.getenv("DB_USER")
DB_PASS   = os.getenv("DB_PASS")
DB_DSN    = os.getenv("DB_DSN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("library")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = RotatingFileHandler(
    "logs/library.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)