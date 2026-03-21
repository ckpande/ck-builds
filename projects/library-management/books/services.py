import oracledb as orc
from config import logger
from .dao import BookDAO
from .models import Book


def add_book(bno: int, bname: str, price: float, pub: str) -> tuple[bool, str]:
    if bno <= 0:
        return False, "Book Number must be greater than 0."
    if not bname.strip() or not pub.strip():
        return False, "Book Name and Publication cannot be blank."
    if price <= 0:
        return False, "Price must be greater than 0."

    book = Book(bno, bname.strip(), price, pub.strip())
    try:
        BookDAO.insert(book)
        return True, f"Book '{bname}' added successfully."
    except orc.DatabaseError as e:
        error, = e.args
        if error.code == 1:
            return False, f"Book Number {bno} already exists. Use a different number."
        logger.error(f"Unexpected DB error in add_book: {e}", exc_info=True)
        return False, "Database error occurred. Check logs/library.log for details."


def update_book_price(bno: int, new_price: float) -> tuple[bool, str]:
    if bno <= 0:
        return False, "Book Number must be greater than 0."
    if new_price <= 0:
        return False, "Price must be greater than 0."
    try:
        rows = BookDAO.update_price(bno, new_price)
        if rows == 0:
            return False, f"No book with ID {bno} found."
        return True, f"Book {bno} price updated to Rs.{new_price:,.2f} successfully."
    except orc.DatabaseError as e:
        logger.error(f"Update book price error: {e}", exc_info=True)
        return False, "Database error occurred. Check logs/library.log for details."


def delete_book(bno: int) -> tuple[bool, str]:
    if bno <= 0:
        return False, "Book Number must be greater than 0."
    try:
        rows = BookDAO.delete(bno)
        if rows == 0:
            return False, f"No book with ID {bno} found."
        return True, f"Book {bno} deleted successfully."
    except orc.DatabaseError as e:
        logger.error(f"Delete book error: {e}", exc_info=True)
        return False, "Database error occurred. Check logs/library.log for details."


def search_book(bno: int):
    if bno <= 0:
        return None
    try:
        return BookDAO.find_by_id(bno)
    except orc.DatabaseError as e:
        logger.error(f"Search book error: {e}", exc_info=True)
        return None


def list_books():
    try:
        return BookDAO.find_all()
    except orc.DatabaseError as e:
        logger.error(f"List books error: {e}", exc_info=True)
        return []