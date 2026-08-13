"""Confidence value type.

A generic decimal confidence score constrained to the inclusive range
[0, 1]. Kept as a distinct type from :class:`~quant_os.core.types.probability.Probability`
so that future domain code cannot accidentally interchange a statistical
probability with a subjective/model confidence score.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from quant_os.core.validation import validate_decimal


@dataclass(frozen=True, slots=True)
class Confidence:
    """An immutable confidence score in the inclusive range [0, 1].

    Attributes:
        value: The confidence value, e.g. ``Decimal("0.9")``.
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
        """Return the confidence as a plain string."""
        return str(self.value)
