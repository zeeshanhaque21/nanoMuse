"""Database shutdown must serialize with background notice transactions."""

import threading
from concurrent.futures import ThreadPoolExecutor

from nanomuse_cloud.db import Database


def test_close_holds_the_transaction_lock():
    db = Database(":memory:")
    connection = db._conn

    class RecordingLock:
        def __init__(self):
            self.lock = threading.RLock()
            self.owner = None

        def __enter__(self):
            self.lock.acquire()
            self.owner = threading.get_ident()

        def __exit__(self, *_):
            self.owner = None
            self.lock.release()

    lock = RecordingLock()
    db._lock = lock

    class CheckedConnection:
        def close(self):
            assert lock.owner == threading.get_ident(), "close bypassed the transaction lock"
            connection.close()

    db._conn = CheckedConnection()
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            with lock:
                closing = pool.submit(db.close)
            closing.result(timeout=5)
    finally:
        connection.close()
