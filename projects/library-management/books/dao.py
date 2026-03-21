import oracledb as orc
from db_pool import get_connection
from config import logger
from .models import Book


class BookDAO:

    @staticmethod
    def insert(book: Book) -> int:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO LIBRARY (BNO, BNAME, PRICE, PUB)
                    VALUES (:1, :2, :3, :4)
                """, (book.bno, book.bname, book.price, book.pub))
                conn.commit()
                logger.info(f"Inserted book: {book.bno} - {book.bname}")
                return cur.rowcount
        except orc.DatabaseError as e:
            conn.rollback()
            logger.error(f"Insert failed for book {book.bno}: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    @staticmethod
    def update_price(bno: int, new_price: float) -> int:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE LIBRARY SET PRICE = :price WHERE BNO = :bno",
                    {"price": new_price, "bno": bno}
                )
                conn.commit()
                logger.info(f"Updated book {bno} price to {new_price}")
                return cur.rowcount
        except orc.DatabaseError as e:
            conn.rollback()
            logger.error(f"Update failed for book {bno}: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    @staticmethod
    def delete(bno: int) -> int:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM LIBRARY WHERE BNO = :bno",
                    {"bno": bno}
                )
                conn.commit()
                logger.info(f"Deleted book {bno}")
                return cur.rowcount
        except orc.DatabaseError as e:
            conn.rollback()
            logger.error(f"Delete failed for book {bno}: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    @staticmethod
    def find_by_id(bno: int):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT BNO, BNAME, PRICE, PUB FROM LIBRARY WHERE BNO = :bno",
                    {"bno": bno}
                )
                row = cur.fetchone()
                if row:
                    return Book(bno=row[0], bname=row[1], price=float(row[2]), pub=row[3])
                return None
        except orc.DatabaseError as e:
            logger.error(f"Find by id failed for {bno}: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    @staticmethod
    def find_all():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT BNO, BNAME, PRICE, PUB FROM LIBRARY ORDER BY BNO"
                )
                rows = cur.fetchall()
                return [
                    Book(bno=r[0], bname=r[1], price=float(r[2]), pub=r[3])
                    for r in rows
                ]
        except orc.DatabaseError as e:
            logger.error(f"Find all failed: {e}", exc_info=True)
            raise
        finally:
            conn.close()
