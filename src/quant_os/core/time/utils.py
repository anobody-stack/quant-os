"""Timezone-aware time utilities.

All datetimes produced or accepted by these utilities are UTC and
timezone-aware. Naive datetimes are treated as invalid input.
"""

from __future__ import annotations

from datetime import UTC, datetime

from quant_os.core.exceptions import ValidationError


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime.

    Returns:
        The current UTC datetime, with ``tzinfo`` set to :data:`datetime.UTC`.
    """
    return datetime.now(UTC)


def to_iso(value: datetime) -> str:
    """Convert a timezone-aware datetime to an ISO 8601 string.

    Args:
        value: The datetime to convert. Must be timezone-aware.

    Returns:
        The ISO 8601 string representation of ``value``.

    Raises:
        ValidationError: If ``value`` is naive (lacks timezone information).
    """
    validate_timezone_aware(value)
    return value.isoformat()


def from_iso(value: str) -> datetime:
    """Parse an ISO 8601 string into a timezone-aware datetime.

    Args:
        value: The ISO 8601 formatted string to parse.

    Returns:
        The parsed, timezone-aware datetime.

    Raises:
        ValidationError: If ``value`` cannot be parsed, or parses to a
            naive datetime.
    """
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(
            "value is not a valid ISO 8601 datetime string",
            cause=exc,
            context={"value": value},
        ) from exc
    validate_timezone_aware(parsed)
    return parsed


def validate_timezone_aware(value: datetime) -> datetime:
    """Validate that a datetime is timezone-aware.

    Args:
        value: The datetime to validate.

    Returns:
        The same datetime, unchanged.

    Raises:
        ValidationError: If ``value`` is naive (lacks timezone information).
    """
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValidationError(
            "datetime must be timezone-aware",
            context={"value": value},
        )
    return value


def parse_datetime(value: str, fmt: str) -> datetime:
    """Parse a datetime string using an explicit format, requiring UTC.

    The format string must include timezone information (e.g. ``%z``)
    so the parsed result is timezone-aware.

    Args:
        value: The datetime string to parse.
        fmt: The ``strptime``-compatible format string.

    Returns:
        The parsed, timezone-aware datetime.

    Raises:
        ValidationError: If ``value`` does not match ``fmt``, or the parsed
            result is naive.
    """
    try:
        parsed = datetime.strptime(value, fmt)
    except ValueError as exc:
        raise ValidationError(
            "value does not match the given datetime format",
            cause=exc,
            context={"value": value, "format": fmt},
        ) from exc
    validate_timezone_aware(parsed)
    return parsed


def format_datetime(value: datetime, fmt: str) -> str:
    """Format a timezone-aware datetime using an explicit format string.

    Args:
        value: The datetime to format. Must be timezone-aware.
        fmt: The ``strftime``-compatible format string.

    Returns:
        The formatted string.

    Raises:
        ValidationError: If ``value`` is naive.
    """
    validate_timezone_aware(value)
    return value.strftime(fmt)
