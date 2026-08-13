"""TimeFrame value type.

A generic enumeration of fixed durations. This is infrastructure-level: it
represents "a duration bucket" and carries no market, candle, or trading
semantics. Any future subsystem needing a notion of "how much time" can
reuse it.
"""

from __future__ import annotations

from enum import Enum


class TimeFrame(Enum):
    """A fixed duration, expressed in seconds via its value.

    Members are named for readability; the underlying value is always the
    duration in whole seconds.
    """

    SECOND_1 = 1
    SECOND_5 = 5
    SECOND_15 = 15
    SECOND_30 = 30
    MINUTE_1 = 60
    MINUTE_5 = 5 * 60
    MINUTE_15 = 15 * 60
    MINUTE_30 = 30 * 60
    HOUR_1 = 60 * 60
    HOUR_4 = 4 * 60 * 60
    DAY_1 = 24 * 60 * 60
    WEEK_1 = 7 * 24 * 60 * 60

    @property
    def seconds(self) -> int:
        """Return the duration represented by this timeframe, in seconds.

        Returns:
            The number of seconds in this timeframe.
        """
        return self.value
