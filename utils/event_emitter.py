# event_emitter.py
# Chandrakant Pande - ckpande

import logging
from collections import defaultdict

log = logging.getLogger("event_emitter")


class EventEmitter:
    def __init__(self):
        self._listeners = defaultdict(list)

    def on(self, event, callback):
        self._listeners[event].append(callback)
        log.debug("listener registered: %s -> %s", event, callback.__name__)

    def off(self, event, callback):
        try:
            self._listeners[event].remove(callback)
            log.debug("listener removed: %s -> %s", event, callback.__name__)
        except ValueError:
            log.warning("off() unregistered callback: %s -> %s", event, callback.__name__)

    def emit(self, event, *args, **kwargs):
        listeners = self._listeners.get(event, [])
        log.info("emitting event: %s, listeners: %d", event, len(listeners))
        for cb in listeners:
            try:
                cb(*args, **kwargs)
            except Exception:
                log.exception("callback error for event %s: %s", event, cb.__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    ee = EventEmitter()


    def update_inventory(book_id):
        print(f"[DB] Book {book_id} inventory updated.")


    def charge_late_fee(book_id):
        raise ConnectionError("Stripe gateway down")


    def send_email(book_id):
        print(f"[EMAIL] Receipt for {book_id} sent.")


    ee.on("book.returned", update_inventory)
    ee.on("book.returned", charge_late_fee)
    ee.on("book.returned", send_email)

    print("\n--- Emitting (one broken listener) ---")
    ee.emit("book.returned", "B-9921")
