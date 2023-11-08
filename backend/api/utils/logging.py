import logging
from typing import Self


class EndpointFilter(logging.Filter):
    def __init__(self: Self, path: str) -> None:
        super().__init__()
        self._path = path

    def filter(self: Self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1
