import asyncio

class MySemaphore:
    """
    Compatibility wrapper around asyncio.Semaphore.
    The original custom implementation breaks asyncio semantics
    on Python 3.11+, so we delegate to native asyncio primitives.
    """
    def __init__(self, value=1):
        self._sem = asyncio.Semaphore(value)

    async def acquire(self, count=1):
        for _ in range(count):
            await self._sem.acquire()
        return True

    def release(self, count=1):
        for _ in range(count):
            self._sem.release()

    # Compatibility helpers used by joycontrol
    def increase(self, value):
        self.release(value)

    def reduce(self, value):
        # Dynamic reduction is not needed by joycontrol; noop
        pass

    def get_value(self):
        return self._sem._value

    def get_aquired(self):
        return 0


class MyBoundedSemaphore:
    """
    Compatibility wrapper around asyncio.BoundedSemaphore.
    """
    def __init__(self, limit=1, value=None):
        initial = limit if value is None else value
        self._limit = limit
        self._sem = asyncio.BoundedSemaphore(initial)

    async def acquire(self, count=1):
        for _ in range(count):
            await self._sem.acquire()
        return True

    def release(self, count=1, best_effort=False):
        for _ in range(count):
            try:
                self._sem.release()
            except ValueError:
                if not best_effort:
                    raise

    # Compatibility helpers
    def increase(self, value):
        self.release(value, best_effort=True)

    def reduce(self, value):
        # Not required by joycontrol
        pass

    def get_value(self):
        return self._sem._value

    def get_aquired(self):
        return 0

    def get_limit(self):
        return self._limit

    def set_limit(self, value):
        self._limit = value
