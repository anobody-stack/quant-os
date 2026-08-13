"""Structured logging infrastructure for QuantOS.

No module should use `print()`; use :func:`get_logger` instead, after
calling :func:`configure_logging` once at process startup.
"""

from quant_os.core.logging.factory import configure_logging, get_logger
from quant_os.core.logging.formatters import ColoredConsoleFormatter, JSONFormatter

__all__ = [
    "ColoredConsoleFormatter",
    "JSONFormatter",
    "configure_logging",
    "get_logger",
]
