"""Logging configuration and logger factory.

Provides a single entry point, :func:`configure_logging`, to set up
console and optional file handlers for the ``quant_os`` logger hierarchy,
and :func:`get_logger` for modules to obtain a configured logger. No
module in QuantOS should call `print()` for operational output — use
:func:`get_logger` instead.
"""

from __future__ import annotations

import logging
from pathlib import Path

from quant_os.core.config.log_level import LogLevel
from quant_os.core.exceptions import InfrastructureError
from quant_os.core.logging.formatters import ColoredConsoleFormatter, JSONFormatter

_ROOT_LOGGER_NAME = "quant_os"


def configure_logging(
    *,
    level: LogLevel = LogLevel.INFO,
    json_format: bool = False,
    log_file: Path | None = None,
    colored: bool = True,
) -> None:
    """Configure the ``quant_os`` logger hierarchy.

    This should be called once, near process startup. Calling it again
    replaces any previously configured handlers on the ``quant_os``
    logger, so it is safe to call repeatedly (e.g. in tests).

    Args:
        level: Minimum log level to emit.
        json_format: If True, emit structured JSON log lines instead of
            colored human-readable console output.
        log_file: Optional file path to also write logs to. Parent
            directories are created if they do not exist.
        colored: If True (and ``json_format`` is False), colorize console
            output by level. Ignored when ``json_format`` is True.

    Raises:
        InfrastructureError: If ``log_file``'s parent directory cannot be
            created, or the file cannot be opened for writing.
    """
    logger = logging.getLogger(_ROOT_LOGGER_NAME)
    logger.setLevel(level.value)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    elif colored:
        console_handler.setFormatter(ColoredConsoleFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
    logger.addHandler(console_handler)

    if log_file is not None:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
        except OSError as exc:
            raise InfrastructureError(
                f"Unable to open log file for writing: {log_file}",
                cause=exc,
                context={"log_file": str(log_file)},
            ) from exc
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a logger scoped under the ``quant_os`` logger hierarchy.

    Args:
        name: The name of the requesting module, conventionally
            ``__name__``.

    Returns:
        A logger named ``quant_os.<name>`` (or simply ``quant_os`` if
        ``name`` already equals the root logger name), inheriting handlers
        and level from :func:`configure_logging`.
    """
    if name == _ROOT_LOGGER_NAME or name.startswith(f"{_ROOT_LOGGER_NAME}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")
