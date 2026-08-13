"""Market data timeframes.

Distinct from :class:`quant_os.core.types.TimeFrame`: this enum includes
``TICK`` (not a fixed duration) and ``MONTHLY`` (a variable-length
duration), neither of which fits the generic, fixed-seconds design of the
core value type.
"""

from __future__ import annotations

from enum import StrEnum


class TimeFrame(StrEnum):
    """A market data granularity, from raw ticks up to monthly bars."""

    TICK = "tick"
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1mo"

    @property
    def seconds(self) -> int | None:
        """The fixed duration of this timeframe in seconds, if it has one.

        Returns:
            The duration in seconds, or ``None`` for :attr:`TICK` (no
            fixed duration) and :attr:`MN1` (variable-length calendar
            month).
        """
        return _SECONDS.get(self)


_SECONDS: dict[TimeFrame, int] = {
    TimeFrame.M1: 60,
    TimeFrame.M5: 5 * 60,
    TimeFrame.M15: 15 * 60,
    TimeFrame.M30: 30 * 60,
    TimeFrame.H1: 60 * 60,
    TimeFrame.H4: 4 * 60 * 60,
    TimeFrame.D1: 24 * 60 * 60,
    TimeFrame.W1: 7 * 24 * 60 * 60,
}
