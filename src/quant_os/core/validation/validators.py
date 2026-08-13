"""Reusable validation helpers.

Each function validates a single value against a set of constraints and
raises :class:`~quant_os.core.exceptions.ValidationError` on failure. These
helpers contain no business rules — only generic structural and range
validation reused across the codebase.
"""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from quant_os.core.exceptions import ValidationError


def validate_numeric(
    value: Any,
    *,
    field_name: str,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
) -> int | float:
    """Validate that a value is numeric and within an optional inclusive range.

    Args:
        value: The value to validate.
        field_name: Name of the field being validated, used in error messages.
        minimum: Optional inclusive lower bound.
        maximum: Optional inclusive upper bound.

    Returns:
        The validated value, unchanged.

    Raises:
        ValidationError: If ``value`` is not numeric, or falls outside the
            given bounds.
    """
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValidationError(
            f"{field_name} must be numeric",
            context={"field_name": field_name, "value": value},
        )
    if minimum is not None and value < minimum:
        raise ValidationError(
            f"{field_name} must be >= {minimum}",
            context={"field_name": field_name, "value": value, "minimum": minimum},
        )
    if maximum is not None and value > maximum:
        raise ValidationError(
            f"{field_name} must be <= {maximum}",
            context={"field_name": field_name, "value": value, "maximum": maximum},
        )
    return value


def validate_string(
    value: Any,
    *,
    field_name: str,
    min_length: int = 0,
    max_length: int | None = None,
    pattern: str | None = None,
) -> str:
    """Validate a string's type, length, and optional pattern.

    Args:
        value: The value to validate.
        field_name: Name of the field being validated, used in error messages.
        min_length: Minimum allowed length (inclusive). Defaults to 0.
        max_length: Optional maximum allowed length (inclusive).
        pattern: Optional regular expression the value must fully match.

    Returns:
        The validated string, unchanged.

    Raises:
        ValidationError: If ``value`` is not a string, violates the length
            bounds, or does not match ``pattern``.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"{field_name} must be a string",
            context={"field_name": field_name, "value": value},
        )
    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must have length >= {min_length}",
            context={"field_name": field_name, "value": value, "min_length": min_length},
        )
    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"{field_name} must have length <= {max_length}",
            context={"field_name": field_name, "value": value, "max_length": max_length},
        )
    if pattern is not None and re.fullmatch(pattern, value) is None:
        raise ValidationError(
            f"{field_name} does not match required pattern",
            context={"field_name": field_name, "value": value, "pattern": pattern},
        )
    return value


def validate_decimal(
    value: Any,
    *,
    field_name: str,
    minimum: Decimal | None = None,
    maximum: Decimal | None = None,
) -> Decimal:
    """Validate and coerce a value into a :class:`~decimal.Decimal`.

    Args:
        value: The value to validate and convert. May be a ``Decimal``,
            ``int``, or numeric ``str``.
        field_name: Name of the field being validated, used in error messages.
        minimum: Optional inclusive lower bound.
        maximum: Optional inclusive upper bound.

    Returns:
        The value as a validated ``Decimal``.

    Raises:
        ValidationError: If ``value`` cannot be converted to ``Decimal`` or
            falls outside the given bounds.
    """
    if isinstance(value, bool):
        raise ValidationError(
            f"{field_name} must be a Decimal, int, or numeric string",
            context={"field_name": field_name, "value": value},
        )
    if isinstance(value, Decimal):
        decimal_value = value
    else:
        try:
            decimal_value = Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError(
                f"{field_name} must be a Decimal, int, or numeric string",
                cause=exc,
                context={"field_name": field_name, "value": value},
            ) from exc

    if minimum is not None and decimal_value < minimum:
        raise ValidationError(
            f"{field_name} must be >= {minimum}",
            context={"field_name": field_name, "value": decimal_value, "minimum": minimum},
        )
    if maximum is not None and decimal_value > maximum:
        raise ValidationError(
            f"{field_name} must be <= {maximum}",
            context={"field_name": field_name, "value": decimal_value, "maximum": maximum},
        )
    return decimal_value


def validate_datetime(value: Any, *, field_name: str, require_tz_aware: bool = True) -> datetime:
    """Validate a datetime value, optionally requiring timezone awareness.

    Args:
        value: The value to validate.
        field_name: Name of the field being validated, used in error messages.
        require_tz_aware: If True (default), the datetime must be
            timezone-aware.

    Returns:
        The validated datetime, unchanged.

    Raises:
        ValidationError: If ``value`` is not a ``datetime``, or is naive
            when ``require_tz_aware`` is True.
    """
    if not isinstance(value, datetime):
        raise ValidationError(
            f"{field_name} must be a datetime",
            context={"field_name": field_name, "value": value},
        )
    if require_tz_aware and (value.tzinfo is None or value.tzinfo.utcoffset(value) is None):
        raise ValidationError(
            f"{field_name} must be timezone-aware",
            context={"field_name": field_name, "value": value},
        )
    return value


def validate_uuid(value: Any, *, field_name: str) -> UUID:
    """Validate and coerce a value into a :class:`~uuid.UUID`.

    Args:
        value: The value to validate. May be a ``UUID`` or a string
            representation of one.
        field_name: Name of the field being validated, used in error messages.

    Returns:
        The value as a validated ``UUID``.

    Raises:
        ValidationError: If ``value`` cannot be interpreted as a valid UUID.
    """
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValidationError(
                f"{field_name} must be a valid UUID",
                cause=exc,
                context={"field_name": field_name, "value": value},
            ) from exc
    raise ValidationError(
        f"{field_name} must be a UUID or UUID string",
        context={"field_name": field_name, "value": value},
    )
