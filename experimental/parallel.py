from collections.abc import Generator
from concurrent.futures import Future
from typing import Generic, TypeVar

T = TypeVar("T", bound=object)
# `T` can by anything except None


class ParSet(Generic[T]):
    def __init__(self) -> None:
        self._items: set[Future[T]] = set()
        self._finished = False

    def add(self, item: Future[T]) -> None:
        assert self._finished is False
        self._items.add(item)

    def finish(self) -> None:
        assert self._finished is False
        self._finished = True

    def pop(self) -> T | None:
        if len(self._items) > 0:
            for future in self._items:
                if future.done():
                    result = future.result()
                    assert result is not None  # should not be possible
                    return result

            # TODO: wait instead of returning None
            return None

        if self._finished:
            return None

        # TODO: wait instead of returning None
        return None
