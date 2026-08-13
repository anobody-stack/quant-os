"""Application environment enumeration."""

from __future__ import annotations

from enum import StrEnum


class Environment(StrEnum):
    """The runtime environment QuantOS is executing in."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
