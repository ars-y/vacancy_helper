import asyncio


class EventLoopContextManager(asyncio.AbstractEventLoop):
    """Context manager for event loop."""

    def __init__(self) -> None:
        super().__init__()
        self._loop: asyncio.AbstractEventLoop | None = None

    def __enter__(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        return self._loop

    def __exit__(self, *exc_info):
        self._loop.close()


class EventLimiter:
    """Limit event with delay."""

    def __init__(self, delay: int | float) -> None:
        self._delay = delay
        self._event: asyncio.Event = asyncio.Event()

        self._event.set()

    async def wait(self):
        while not self._event.is_set():
            await self._event.wait()

        self._event.clear()
        asyncio.get_event_loop().call_later(self._delay, self._event.set)
