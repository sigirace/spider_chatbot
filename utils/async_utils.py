from typing import AsyncIterator, TypeVar

T = TypeVar("T")


async def aenumerate(aiter: AsyncIterator[T], start: int = 0):
    """`enumerate` 의 async 버전."""
    idx = start
    async for item in aiter:
        yield idx, item
        idx += 1
