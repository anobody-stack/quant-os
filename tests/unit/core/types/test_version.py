"""Unit tests for the Version value type."""

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Version


def test_valid_version() -> None:
    version = Version(1, 2, 3)
    assert (version.major, version.minor, version.patch) == (1, 2, 3)


def test_negative_component_raises() -> None:
    with pytest.raises(ValidationError):
        Version(-1, 0, 0)


def test_non_int_component_raises() -> None:
    with pytest.raises(ValidationError):
        Version(1.5, 0, 0)  # type: ignore[arg-type]


def test_bool_component_raises() -> None:
    with pytest.raises(ValidationError):
        Version(True, 0, 0)  # type: ignore[arg-type]


def test_parse_valid_string() -> None:
    assert Version.parse("1.2.3") == Version(1, 2, 3)


def test_parse_rejects_wrong_segment_count() -> None:
    with pytest.raises(ValidationError):
        Version.parse("1.2")


def test_parse_rejects_non_integer_segments() -> None:
    with pytest.raises(ValidationError):
        Version.parse("1.x.3")


def test_is_immutable() -> None:
    version = Version(1, 0, 0)
    with pytest.raises(AttributeError):
        version.major = 2  # type: ignore[misc]


def test_str_representation() -> None:
    assert str(Version(1, 2, 3)) == "1.2.3"
