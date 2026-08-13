"""Unit tests for EventType and EventPriority."""

from quant_os.events.enums import EventPriority, EventType


def test_event_type_members_are_strings() -> None:
    assert EventType.NEWS_RECEIVED == "news_received"
    assert EventType.ORDER_FILLED == "order_filled"


def test_event_priority_ordering() -> None:
    assert EventPriority.LOW < EventPriority.NORMAL < EventPriority.HIGH < EventPriority.CRITICAL


def test_event_priority_values() -> None:
    assert EventPriority.LOW == 0
    assert EventPriority.CRITICAL == 3
