"""Unit tests for timezone-aware time utilities."""

from datetime import UTC, datetime

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.time import (
    format_datetime,
    from_iso,
    parse_datetime,
    to_iso,
    utc_now,
    validate_timezone_aware,
)


def test_utc_now_is_timezone_aware() -> None:
    """utc_now() returns a timezone-aware datetime in UTC."""
    now = utc_now()
    assert now.tzinfo is not None
    offset = now.tzinfo.utcoffset(now)
    assert offset is not None
    assert offset.total_seconds() == 0


def test_to_iso_round_trips_with_from_iso() -> None:
    """A datetime converted to ISO and back is equal to the original."""
    original = datetime(2024, 6, 15, 12, 30, 0, tzinfo=UTC)
    iso_string = to_iso(original)
    restored = from_iso(iso_string)
    assert restored == original


def test_to_iso_rejects_naive_datetime() -> None:
    """to_iso raises for naive datetimes."""
    with pytest.raises(ValidationError):
        to_iso(datetime(2024, 1, 1))


def test_from_iso_rejects_invalid_string() -> None:
    """from_iso raises for unparsable strings."""
    with pytest.raises(ValidationError):
        from_iso("not-a-date")


def test_from_iso_rejects_naive_result() -> None:
    """from_iso raises when the parsed string has no timezone offset."""
    with pytest.raises(ValidationError):
        from_iso("2024-01-01T00:00:00")


def test_validate_timezone_aware_accepts_aware() -> None:
    """validate_timezone_aware returns the value unchanged when aware."""
    value = datetime.now(UTC)
    assert validate_timezone_aware(value) is value


def test_validate_timezone_aware_rejects_naive() -> None:
    """validate_timezone_aware raises for naive datetimes."""
    with pytest.raises(ValidationError):
        validate_timezone_aware(datetime(2024, 1, 1))


def test_parse_datetime_valid() -> None:
    """parse_datetime parses a string matching the given format with tz offset."""
    result = parse_datetime("2024-01-01 00:00:00 +0000", "%Y-%m-%d %H:%M:%S %z")
    assert result.year == 2024
    assert result.tzinfo is not None


def test_parse_datetime_rejects_mismatched_format() -> None:
    """parse_datetime raises when the string does not match the format."""
    with pytest.raises(ValidationError):
        parse_datetime("not-a-date", "%Y-%m-%d %H:%M:%S %z")


def test_parse_datetime_rejects_naive_result() -> None:
    """parse_datetime raises when the format string omits timezone info."""
    with pytest.raises(ValidationError):
        parse_datetime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")


def test_format_datetime_valid() -> None:
    """format_datetime formats a timezone-aware datetime using the given format."""
    value = datetime(2024, 1, 1, tzinfo=UTC)
    assert format_datetime(value, "%Y-%m-%d") == "2024-01-01"


def test_format_datetime_rejects_naive() -> None:
    """format_datetime raises for naive datetimes."""
    with pytest.raises(ValidationError):
        format_datetime(datetime(2024, 1, 1), "%Y-%m-%d")
