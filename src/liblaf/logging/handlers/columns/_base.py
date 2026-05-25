"""Base interface for Rich handler columns."""

import abc
import logging

from rich.text import Text


class RichHandlerColumn(abc.ABC):
    """Render one optional prefix column for a log record."""

    @abc.abstractmethod
    def render(self, record: logging.LogRecord, /) -> Text | None:
        """Render a column for `record`, or return `None` to omit it."""
        ...
