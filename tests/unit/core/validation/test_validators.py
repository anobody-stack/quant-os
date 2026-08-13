"""Unit tests for reusable validation helpers."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.validation import (
    validate_datetime,
    validate_decimal,
    validate_numeric,
    validate_string,
    validate_uuid,
)


class TestValidateNumeric:
    """Tests for validate_numeric."""

    def test_valid_int(self) -> None:
        assert validate_numeric(5, field_name="x") == 5

    def test_valid_float(self) -> None:
        assert validate_numeric(5.5, field_name="x") == 5.5

    def test_rejects_bool(self) -> None:
        with pytest.raises(ValidationError):
            validate_numeric(True, field_name="x")

    def test_rejects_non_numeric(self) -> None:
        with pytest.raises(ValidationError):
            validate_numeric("not a number", field_name="x")

    def test_rejects_below_minimum(self) -> None:
        with pytest.raises(ValidationError):
            validate_numeric(1, field_name="x", minimum=5)

    def test_rejects_above_maximum(self) -> None:
        with pytest.raises(ValidationError):
            validate_numeric(10, field_name="x", maximum=5)

    def test_accepts_within_bounds(self) -> None:
        assert validate_numeric(5, field_name="x", minimum=0, maximum=10) == 5


class TestValidateString:
    """Tests for validate_string."""

    def test_valid_string(self) -> None:
        assert validate_string("hello", field_name="x") == "hello"

    def test_rejects_non_string(self) -> None:
        with pytest.raises(ValidationError):
            validate_string(123, field_name="x")

    def test_rejects_too_short(self) -> None:
        with pytest.raises(ValidationError):
            validate_string("ab", field_name="x", min_length=3)

    def test_rejects_too_long(self) -> None:
        with pytest.raises(ValidationError):
            validate_string("abcdef", field_name="x", max_length=3)

    def test_rejects_pattern_mismatch(self) -> None:
        with pytest.raises(ValidationError):
            validate_string("abc", field_name="x", pattern=r"[0-9]+")

    def test_accepts_pattern_match(self) -> None:
        assert validate_string("123", field_name="x", pattern=r"[0-9]+") == "123"


class TestValidateDecimal:
    """Tests for validate_decimal."""

    def test_accepts_decimal(self) -> None:
        assert validate_decimal(Decimal("1.5"), field_name="x") == Decimal("1.5")

    def test_accepts_int(self) -> None:
        assert validate_decimal(5, field_name="x") == Decimal("5")

    def test_accepts_numeric_string(self) -> None:
        assert validate_decimal("2.25", field_name="x") == Decimal("2.25")

    def test_rejects_bool(self) -> None:
        with pytest.raises(ValidationError):
            validate_decimal(True, field_name="x")

    def test_rejects_invalid_string(self) -> None:
        with pytest.raises(ValidationError):
            validate_decimal("not-a-number", field_name="x")

    def test_rejects_below_minimum(self) -> None:
        with pytest.raises(ValidationError):
            validate_decimal(Decimal("1"), field_name="x", minimum=Decimal("5"))

    def test_rejects_above_maximum(self) -> None:
        with pytest.raises(ValidationError):
            validate_decimal(Decimal("10"), field_name="x", maximum=Decimal("5"))


class TestValidateDatetime:
    """Tests for validate_datetime."""

    def test_accepts_aware_datetime(self) -> None:
        value = datetime.now(UTC)
        assert validate_datetime(value, field_name="x") is value

    def test_rejects_non_datetime(self) -> None:
        with pytest.raises(ValidationError):
            validate_datetime("not a datetime", field_name="x")

    def test_rejects_naive_datetime_by_default(self) -> None:
        with pytest.raises(ValidationError):
            validate_datetime(datetime(2024, 1, 1), field_name="x")

    def test_allows_naive_when_not_required(self) -> None:
        value = datetime(2024, 1, 1)
        assert validate_datetime(value, field_name="x", require_tz_aware=False) is value


class TestValidateUuid:
    """Tests for validate_uuid."""

    def test_accepts_uuid_instance(self) -> None:
        value = uuid4()
        assert validate_uuid(value, field_name="x") is value

    def test_accepts_uuid_string(self) -> None:
        value = uuid4()
        assert validate_uuid(str(value), field_name="x") == value

    def test_rejects_invalid_string(self) -> None:
        with pytest.raises(ValidationError):
            validate_uuid("not-a-uuid", field_name="x")

    def test_rejects_wrong_type(self) -> None:
        with pytest.raises(ValidationError):
            validate_uuid(12345, field_name="x")

    def test_returns_uuid_type(self) -> None:
        value = uuid4()
        result = validate_uuid(str(value), field_name="x")
        assert isinstance(result, UUID)
