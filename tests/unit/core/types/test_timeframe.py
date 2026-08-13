"""Unit tests for the TimeFrame value type."""

from quant_os.core.types import TimeFrame


def test_seconds_property_matches_value() -> None:
    assert TimeFrame.MINUTE_1.seconds == 60


def test_hour_1_equals_3600_seconds() -> None:
    assert TimeFrame.HOUR_1.seconds == 3600


def test_day_1_equals_86400_seconds() -> None:
    assert TimeFrame.DAY_1.seconds == 86400


def test_week_1_equals_604800_seconds() -> None:
    assert TimeFrame.WEEK_1.seconds == 604800


def test_members_are_distinct() -> None:
    assert TimeFrame.SECOND_1 != TimeFrame.SECOND_5
