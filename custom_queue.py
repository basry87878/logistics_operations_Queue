import threading


class Queue:
    """
    A thread-safe FIFO Queue implementation using a Python list and a threading lock.
    Used as the shared buffer between the Order Generator (producer)
    and Order Processor (consumer) threads.
    """

    def __init__(self):
        self._buffer = []
        self._lock = threading.Lock()

    def enqueue(self, value):
        """Insert an item at the front of the buffer (FIFO entry point)."""
        with self._lock:
            self._buffer.insert(0, value)

    def dequeue(self):
        """Remove and return the oldest item from the buffer (FIFO exit point)."""
        with self._lock:
            if not self._is_empty_unsafe():
                return self._buffer.pop()
            return None

    def is_empty(self):
        """Thread-safe check — returns True if the queue has no items."""
        with self._lock:
            return self._is_empty_unsafe()

    def size(self):
        """Return the current number of items in the queue."""
        with self._lock:
            return len(self._buffer)

    # Internal helper — only call when the lock is already held
    def _is_empty_unsafe(self):
        return len(self._buffer) == 0

    def __repr__(self):
        with self._lock:
            return f"Queue({list(reversed(self._buffer))})"