import oracledb as orc
from config import logger
from .services import add_book, update_book_price, delete_book, search_book, list_books


def ask_continue(prompt: str) -> bool:
    while True:
        ch = input(prompt).strip().lower()
        if ch == "yes":
            return True
        elif ch == "no":
            return False
        else:
            print("Please enter yes or no.")


def display_menu():
    print("""
    =================================================
                Books Management
    =================================================
        1. Add a New Book
        2. Delete a Book
        3. Update Book Price
        4. Search Book by Number
        5. View All Books
        6. Back to Main Menu
    =================================================""")
    return input("Enter your choice: ").strip()


def run():
    while True:
        choice = display_menu()
        match choice:

            case "1":
                while True:
                    print("-" * 50)
                    try:
                        bno = int(input("Enter Book Number   : "))
                        bname = input("Enter Book Name     : ").strip()
                        price = float(input("Enter Book Price    : "))
                        pub = input("Enter Publication   : ").strip()
                        success, msg = add_book(bno, bname, price, pub)
                        print(msg)
                    except ValueError:
                        print("Input Error: Book Number and Price must be numeric.")
                    except orc.DatabaseError as e:
                        logger.error(f"Unexpected error in add book: {e}", exc_info=True)
                        print("Unexpected database error. Check logs/library.log.")
                    print("-" * 50)
                    if not ask_continue("Do you want to add another book? (yes/no): "):
                        break

            case "2":
                while True:
                    print("-" * 50)
                    try:
                        bno = int(input("Enter Book Number to DELETE: "))
                        confirm = input(f"Are you sure you want to delete book {bno}? (yes/no): ").strip().lower()
                        if confirm == "yes":
                            success, msg = delete_book(bno)
                            print(msg)
                        else:
                            print("Delete cancelled. Book is safe.")
                    except ValueError:
                        print("Input Error: Book Number must be numeric.")
                    except orc.DatabaseError as e:
                        logger.error(f"Unexpected error in delete book: {e}", exc_info=True)
                        print("Unexpected database error. Check logs/library.log.")
                    print("-" * 50)
                    if not ask_continue("Do you want to delete another book? (yes/no): "):
                        break

            case "3":
                while True:
                    print("-" * 50)
                    try:
                        bno = int(input("Enter Book Number to UPDATE: "))
                        new_price = float(input("Enter new price            : "))
                        success, msg = update_book_price(bno, new_price)
                        print(msg)
                    except ValueError:
                        print("Input Error: Book Number and Price must be numeric.")
                    except orc.DatabaseError as e:
                        logger.error(f"Unexpected error in update book: {e}", exc_info=True)
                        print("Unexpected database error. Check logs/library.log.")
                    print("-" * 50)
                    if not ask_continue("Do you want to update another book? (yes/no): "):
                        break

            case "4":
                while True:
                    print("-" * 50)
                    try:
                        bno = int(input("Enter Book Number: "))
                        book = search_book(bno)
                        if book:
                            print("\n" + "=" * 42)
                            print(f"{'  BOOK DETAILS':^42}")
                            print("=" * 42)
                            print(f"  {'Book Number':<14}: {book.bno}")
                            print(f"  {'Book Name':<14}: {book.bname}")
                            print(f"  {'Price':<14}: Rs. {book.price:,.2f}")
                            print(f"  {'Publisher':<14}: {book.pub}")
                            print("=" * 42)
                        else:
                            print(f"Not Found: No book with ID {bno}.")
                    except ValueError:
                        print("Input Error: Book Number must be numeric.")
                    except orc.DatabaseError as e:
                        logger.error(f"Unexpected error in search book: {e}", exc_info=True)
                        print("Unexpected database error. Check logs/library.log.")
                    print("-" * 50)
                    if not ask_continue("Do you want to search another book? (yes/no): "):
                        break

            case "5":
                try:
                    books = list_books()
                    if not books:
                        print("No books found in the library.")
                    else:
                        print("-" * 70)
                        print(f"{'ID':<6}{'Name':<30}{'Price':<15}{'Publisher'}")
                        print("-" * 70)
                        for b in books:
                            print(f"{b.bno:<6}{b.bname:<30}Rs.{b.price:>5,.2f}       {b.pub}")
                        print("-" * 70)
                        print(f"Total: {len(books)} book(s)")
                except orc.DatabaseError as e:
                    logger.error(f"Unexpected error in list books: {e}", exc_info=True)
                    print("Unexpected database error. Check logs/library.log.")

            case "6":
                print("Returning to main menu.")
                break

            case _:
                print("Invalid choice. Please enter a number between 1 and 6.")
