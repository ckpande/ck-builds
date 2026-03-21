import time
import oracledb as orc
from config import logger
from db_pool import init_pool
import books.routes as book_routes


def run_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            func()
            return
        except orc.DatabaseError as e:
            error, = e.args
            if error.code == 60:
                wait = 2 ** attempt
                logger.warning(f"Deadlock detected. Retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                logger.error(f"Database error in {func.__name__}: {e}", exc_info=True)
                print("Unexpected database error. Check logs/library.log.")
                return
    logger.error(f"Function {func.__name__} failed after {max_retries} retries.")
    print("Operation failed after multiple retries. Please try again later.")


def main_menu():
    print("""
    =================================================
            Library Management System
    =================================================
        1. Books Management
        2. Members Management (coming soon)
        3. Loans Management  (coming soon)
        4. Exit
    =================================================""")
    return input("Enter your choice: ").strip()


def main():
    try:
        init_pool()
        logger.info("Application started.")
    except EnvironmentError as e:
        logger.critical(f"Configuration error: {e}")
        print(f"Config Error: {e}")
        return
    except orc.DatabaseError as e:
        logger.critical(f"Failed to initialize database pool: {e}")
        print("Could not connect to database. Check your .env file and Oracle service.")
        return

    while True:
        choice = main_menu()
        match choice:
            case "1":
                run_with_retry(book_routes.run)
            case "2":
                print("Members module not yet implemented.")
            case "3":
                print("Loans module not yet implemented.")
            case "4":
                print("Thank you for using Library Management System. Goodbye!")
                logger.info("Application exit.")
                break
            case _:
                print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
