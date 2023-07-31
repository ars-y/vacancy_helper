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
