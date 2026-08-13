"""Percentage value type.

A generic decimal percentage constrained to the inclusive range [0, 100].
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from quant_os.core.validation import validate_decimal


@dataclass(frozen=True, slots=True)
class Percentage:
    """An immutable percentage value in the inclusive range [0, 100].

    Attributes:
        value: The percentage value, e.g. ``Decimal("12.5")`` for 12.5%.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that the value lies within [0, 100]."""
        object.__setattr__(
            self,
            "value",
            validate_decimal(
                self.value,
                field_name="value",
                minimum=Decimal("0"),
                maximum=Decimal("100"),
            ),
        )

    def as_fraction(self) -> Decimal:
        """Return the percentage expressed as a fraction in [0, 1].

        Returns:
            ``value / 100``.
        """
        return self.value / Decimal("100")

    def __str__(self) -> str:
        """Return the percentage as a string, e.g. ``"12.5%"``."""
        return f"{self.value}%"
