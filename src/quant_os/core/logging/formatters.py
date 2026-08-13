"""Log formatters: structured JSON and colored console output.

Built entirely on the standard library `logging` module — no third-party
logging dependency is introduced.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any, ClassVar


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects.

    Each record includes a UTC ISO 8601 timestamp, level, logger (module)
    name, message, and any exception information present.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            A single-line JSON string representing the record.
        """
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


class ColoredConsoleFormatter(logging.Formatter):
    """Formats log records for human-readable, colored console output.

    Colors are applied via ANSI escape codes and are keyed by log level.
    Each line includes a UTC ISO 8601 timestamp, the logger (module) name,
    the level, and the message.
    """

    _RESET: ClassVar[str] = "\033[0m"
    _LEVEL_COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: "\033[36m",  # cyan
        logging.INFO: "\033[32m",  # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[41m",  # red background
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a colored, human-readable line.

        Args:
            record: The log record to format.

        Returns:
            The formatted log line, with ANSI color codes wrapping the
            level name.
        """
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoformat()
        color = self._LEVEL_COLORS.get(record.levelno, "")
        level = f"{color}{record.levelname}{self._RESET}" if color else record.levelname
        line = f"{timestamp} [{level}] {record.name}: {record.getMessage()}"
        if record.exc_info:
            line = f"{line}\n{self.formatException(record.exc_info)}"
        return line
