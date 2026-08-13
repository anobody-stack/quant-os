"""QuantOS exception hierarchy.

All QuantOS-specific exceptions derive from :class:`QuantOSError`. Every
exception supports a human-readable message, an optional wrapped cause
(the underlying exception that triggered this one), and a free-form
context dictionary carrying diagnostic details (e.g. the offending field
name and value).

This module is purely generic infrastructure. It has no knowledge of any
financial or trading concept.
"""

from __future__ import annotations

from typing import Any


class QuantOSError(Exception):
    """Base class for all QuantOS-specific exceptions.

    Attributes:
        message: Human-readable description of the error.
        cause: The underlying exception that caused this error, if any.
        context: Arbitrary structured diagnostic data relevant to the error.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable description of the error.
            cause: The underlying exception that caused this error, if any.
            context: Arbitrary structured diagnostic data relevant to the
                error. Defaults to an empty dict when not provided.
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.context: dict[str, Any] = dict(context) if context is not None else {}

    def __str__(self) -> str:
        """Return a string representation including context and cause, if present."""
        parts = [self.message]
        if self.context:
            parts.append(f"context={self.context!r}")
        if self.cause is not None:
            parts.append(f"cause={self.cause!r}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Return an unambiguous representation of the exception."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"cause={self.cause!r}, context={self.context!r})"
        )


class ConfigurationError(QuantOSError):
    """Raised when application configuration is missing, invalid, or malformed."""


class ValidationError(QuantOSError):
    """Raised when a value fails validation rules."""


class InfrastructureError(QuantOSError):
    """Raised when an infrastructure-level operation fails.

    Examples include failures in logging setup, identifier generation, or
    other cross-cutting infrastructure concerns.
    """


class DataError(QuantOSError):
    """Raised when data is missing, malformed, or otherwise unusable."""


class SystemError(QuantOSError):
    """Raised for unexpected system-level failures not covered by other exceptions."""
