import asyncio

class AsyncIterZipper:
    def __init__(self, iter1, iter2):
        self.iter1 = iter1
        self.iter2 = iter2

    async def get_next(self, iter):
        try:
            return await iter.__anext__()
        except StopAsyncIteration:
            return None

    async def __aiter__(self):
        return self

    async def __anext__(self):
        value1, value2 = await asyncio.gather(
            self.get_next(self.iter1),
            self.get_next(self.iter2)
        )

        if value1 is None and value2 is None:
            raise StopAsyncIteration
        else:
            return (value1, value2)