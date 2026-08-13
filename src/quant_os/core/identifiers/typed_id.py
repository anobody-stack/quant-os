"""Generic, typed identifier primitive.

:class:`TypedId` wraps a :class:`~uuid.UUID` and is intended as a base class
for future domain-specific identifiers (e.g. an eventual ``InstrumentId``).
It is immutable, hashable, and carries no domain knowledge itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from quant_os.core.validation import validate_uuid


@dataclass(frozen=True, slots=True)
class TypedId:
    """An immutable, typed wrapper around a UUID.

    Subclass this to create domain-specific identifier types with strong
    typing (e.g. ``class InstrumentId(TypedId): pass``), preventing
    accidental interchange of unrelated identifier kinds at the type level.

    Attributes:
        value: The underlying UUID value.
    """

    value: UUID

    def __post_init__(self) -> None:
        """Validate that ``value`` is a proper UUID."""
        validate_uuid(self.value, field_name="value")

    @classmethod
    def generate(cls) -> Self:
        """Generate a new identifier using a random UUID (UUID4).

        Returns:
            A new instance of the calling class wrapping a fresh UUID4.
        """
        return cls(uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """Construct an identifier from its string representation.

        Args:
            raw: The string representation of a UUID.

        Returns:
            A new instance of the calling class wrapping the parsed UUID.

        Raises:
            ValidationError: If ``raw`` is not a valid UUID string.
        """
        return cls(validate_uuid(raw, field_name="raw"))

    def __str__(self) -> str:
        """Return the canonical string representation of the underlying UUID."""
        return str(self.value)
