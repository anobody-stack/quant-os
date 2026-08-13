"""Unit tests for structured logging infrastructure."""

import json
import logging
from pathlib import Path
from types import TracebackType

import pytest

from quant_os.core.config.log_level import LogLevel
from quant_os.core.exceptions import InfrastructureError
from quant_os.core.logging import (
    ColoredConsoleFormatter,
    JSONFormatter,
    configure_logging,
    get_logger,
)

_ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None] | None


def _make_record(
    message: str = "hello", level: int = logging.INFO, exc_info: _ExcInfo = None
) -> logging.LogRecord:
    return logging.LogRecord(
        name="quant_os.test",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=exc_info,
    )


class TestJSONFormatter:
    def test_produces_valid_json(self) -> None:
        record = _make_record("test message")
        formatted = JSONFormatter().format(record)
        payload = json.loads(formatted)
        assert payload["message"] == "test message"
        assert payload["level"] == "INFO"
        assert payload["logger"] == "quant_os.test"
        assert "timestamp" in payload

    def test_includes_exception_info(self) -> None:
        try:
            raise ValueError("boom")
        except ValueError as exc:
            exc_info = (type(exc), exc, exc.__traceback__)
            record = _make_record("failure", level=logging.ERROR, exc_info=exc_info)
        formatted = JSONFormatter().format(record)
        payload = json.loads(formatted)
        assert "exception" in payload
        assert "boom" in payload["exception"]


class TestColoredConsoleFormatter:
    def test_includes_level_and_message(self) -> None:
        record = _make_record("colored message", level=logging.WARNING)
        formatted = ColoredConsoleFormatter().format(record)
        assert "colored message" in formatted
        assert "quant_os.test" in formatted

    def test_includes_exception_info(self) -> None:
        try:
            raise ValueError("boom")
        except ValueError as exc:
            exc_info = (type(exc), exc, exc.__traceback__)
            record = _make_record("failure", level=logging.ERROR, exc_info=exc_info)
        formatted = ColoredConsoleFormatter().format(record)
        assert "boom" in formatted

    def test_unknown_level_has_no_color_wrapper(self) -> None:
        record = _make_record("plain", level=99)
        formatted = ColoredConsoleFormatter().format(record)
        assert "plain" in formatted


class TestConfigureLogging:
    def test_console_only_default(self) -> None:
        configure_logging(level=LogLevel.DEBUG)
        logger = get_logger("quant_os.test.console")
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_json_format(self) -> None:
        configure_logging(level=LogLevel.INFO, json_format=True)
        root = logging.getLogger("quant_os")
        assert any(isinstance(h.formatter, JSONFormatter) for h in root.handlers)

    def test_uncolored_console(self) -> None:
        configure_logging(level=LogLevel.INFO, json_format=False, colored=False)
        root = logging.getLogger("quant_os")
        assert not any(isinstance(h.formatter, ColoredConsoleFormatter) for h in root.handlers)

    def test_reconfiguring_replaces_handlers(self) -> None:
        configure_logging(level=LogLevel.INFO)
        first_handler_count = len(logging.getLogger("quant_os").handlers)
        configure_logging(level=LogLevel.INFO)
        second_handler_count = len(logging.getLogger("quant_os").handlers)
        assert first_handler_count == second_handler_count

    def test_writes_to_log_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "logs" / "quant_os.log"
        configure_logging(level=LogLevel.INFO, log_file=log_file)
        logger = get_logger("quant_os.test.file")
        logger.info("file log message")
        for handler in logging.getLogger("quant_os").handlers:
            handler.flush()
        assert log_file.exists()
        content = log_file.read_text()
        assert "file log message" in content

    def test_invalid_log_file_path_raises_infrastructure_error(self, tmp_path: Path) -> None:
        blocked = tmp_path / "not_a_directory"
        blocked.write_text("occupied")
        bad_path = blocked / "quant_os.log"
        with pytest.raises(InfrastructureError):
            configure_logging(level=LogLevel.INFO, log_file=bad_path)


class TestGetLogger:
    def test_prefixes_module_name(self) -> None:
        logger = get_logger("my_module")
        assert logger.name == "quant_os.my_module"

    def test_root_name_passthrough(self) -> None:
        logger = get_logger("quant_os")
        assert logger.name == "quant_os"

    def test_already_prefixed_name_passthrough(self) -> None:
        logger = get_logger("quant_os.some.module")
        assert logger.name == "quant_os.some.module"
