"""Strongly typed module capabilities.

Modules advertise capabilities instead of exposing implementation
details, allowing the kernel (and other modules) to discover "what can
this module do" without depending on concrete types.
"""

from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    """A capability a QuantOS module may advertise."""

    MARKET_DATA = "market_data"
    NEWS = "news"
    MACRO = "macro"
    RISK = "risk"
    EXECUTION = "execution"
    PORTFOLIO = "portfolio"
    REPORTING = "reporting"
    AI = "ai"
