"""Log level enumeration shared by configuration and logging modules."""

from __future__ import annotations

from enum import StrEnum


class LogLevel(StrEnum):
    """Supported logging verbosity levels, mirroring the stdlib `logging` levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
