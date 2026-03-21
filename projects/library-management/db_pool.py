import oracledb as orc
from config import DB_USER, DB_PASS, DB_DSN, logger

pool = None


def init_pool():
    global pool
    if pool is None:
        if not all([DB_USER, DB_PASS, DB_DSN]):
            raise EnvironmentError(
                "Missing DB credentials. Check your .env file — "
                "DB_USER, DB_PASS, DB_DSN must all be set."
            )
        try:
            pool = orc.create_pool(
                user=DB_USER,
                password=DB_PASS,
                dsn=DB_DSN,
                min=2,
                max=10,
                increment=1
            )
            logger.info("Connection pool created (min=2, max=10).")
        except orc.DatabaseError as e:
            logger.error(f"Failed to create pool: {e}")
            raise


def get_connection():
    if pool is None:
        init_pool()
    try:
        conn = pool.acquire()
        logger.debug("Acquired connection from pool.")
        return conn
    except orc.DatabaseError as e:
        logger.error(f"Failed to acquire connection: {e}")
        raise
