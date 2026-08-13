"""Money value type.

A generic, currency-tagged monetary amount backed by :class:`~decimal.Decimal`.
No business rules (conversion, formatting for display, arithmetic across
currencies) are implemented here — only structural validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from quant_os.core.validation import validate_decimal, validate_string

_CURRENCY_PATTERN = r"[A-Z]{3}"


@dataclass(frozen=True, slots=True)
class Money:
    """An immutable monetary amount tagged with an ISO 4217-shaped currency code.

    Attributes:
        amount: The monetary amount.
        currency: A 3-letter uppercase currency code (e.g. ``"USD"``). Only
            the shape is validated here; no lookup against a real ISO 4217
            registry is performed.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate the amount and currency code."""
        object.__setattr__(self, "amount", validate_decimal(self.amount, field_name="amount"))
        object.__setattr__(
            self,
            "currency",
            validate_string(
                self.currency,
                field_name="currency",
                min_length=3,
                max_length=3,
                pattern=_CURRENCY_PATTERN,
            ),
        )

    def __str__(self) -> str:
        """Return a human-readable representation, e.g. ``"100.00 USD"``."""
        return f"{self.amount} {self.currency}"
