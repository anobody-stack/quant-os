"""Unit tests for the generic TypedId identifier primitive."""

from uuid import UUID, uuid4

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.identifiers import TypedId


class SampleId(TypedId):
    """A concrete TypedId subclass used only for testing."""


def test_generate_creates_valid_id() -> None:
    """generate() produces a TypedId wrapping a valid UUID."""
    identifier = SampleId.generate()
    assert isinstance(identifier.value, UUID)


def test_generate_produces_unique_ids() -> None:
    """Successive calls to generate() produce distinct identifiers."""
    first = SampleId.generate()
    second = SampleId.generate()
    assert first != second


def test_from_string_valid() -> None:
    """from_string() parses a valid UUID string."""
    raw = str(uuid4())
    identifier = SampleId.from_string(raw)
    assert str(identifier) == raw


def test_from_string_invalid_raises() -> None:
    """from_string() raises ValidationError for a malformed UUID string."""
    with pytest.raises(ValidationError):
        SampleId.from_string("not-a-uuid")


def test_direct_construction_validates() -> None:
    """Direct construction with an invalid value raises ValidationError."""
    with pytest.raises(ValidationError):
        SampleId(value="not-a-uuid")  # type: ignore[arg-type]


def test_is_immutable() -> None:
    """TypedId instances are frozen and cannot be mutated after creation."""
    identifier = SampleId.generate()
    with pytest.raises(AttributeError):
        identifier.value = uuid4()  # type: ignore[misc]


def test_equality_based_on_value() -> None:
    """Two TypedIds with the same underlying UUID are equal."""
    value = uuid4()
    assert SampleId(value) == SampleId(value)


def test_str_returns_canonical_uuid_string() -> None:
    """str() returns the canonical string form of the underlying UUID."""
    value = uuid4()
    identifier = SampleId(value)
    assert str(identifier) == str(value)
