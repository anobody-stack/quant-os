"""Probability value type.

A generic decimal probability constrained to the inclusive range [0, 1].
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from quant_os.core.validation import validate_decimal


@dataclass(frozen=True, slots=True)
class Probability:
    """An immutable probability value in the inclusive range [0, 1].

    Attributes:
        value: The probability value, e.g. ``Decimal("0.75")``.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that the value lies within [0, 1]."""
        object.__setattr__(
            self,
            "value",
            validate_decimal(
                self.value,
                field_name="value",
                minimum=Decimal("0"),
                maximum=Decimal("1"),
            ),
        )

    def __str__(self) -> str:
        """Return the probability as a plain string."""
        return str(self.value)
