"""Price value type.

A generic, non-negative decimal price. No business or market semantics are
implemented here — only structural validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from quant_os.core.validation import validate_decimal


@dataclass(frozen=True, slots=True)
class Price:
    """An immutable, non-negative price value.

    Attributes:
        value: The price amount. Must be greater than or equal to zero.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that the price is a non-negative decimal."""
        object.__setattr__(
            self,
            "value",
            validate_decimal(self.value, field_name="value", minimum=Decimal("0")),
        )

    def __str__(self) -> str:
        """Return the price as a plain string."""
        return str(self.value)
