"""Version value type.

A generic semantic-version-shaped identifier (``major.minor.patch``), used
to version configuration schemas, models, or other artifacts across
QuantOS. Not tied to any packaging system.
"""

from __future__ import annotations

from dataclasses import dataclass

from quant_os.core.exceptions import ValidationError
from quant_os.core.validation import validate_numeric


@dataclass(frozen=True, slots=True)
class Version:
    """An immutable ``major.minor.patch`` version identifier.

    Attributes:
        major: Major version component. Must be >= 0.
        minor: Minor version component. Must be >= 0.
        patch: Patch version component. Must be >= 0.
    """

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        """Validate that all components are non-negative integers."""
        for field_name, field_value in (
            ("major", self.major),
            ("minor", self.minor),
            ("patch", self.patch),
        ):
            validated = validate_numeric(field_value, field_name=field_name, minimum=0)
            if not isinstance(validated, int) or isinstance(validated, bool):
                raise ValidationError(
                    f"{field_name} must be an int",
                    context={"field_name": field_name, "value": field_value},
                )

    @classmethod
    def parse(cls, raw: str) -> Version:
        """Parse a version string of the form ``"major.minor.patch"``.

        Args:
            raw: The version string to parse.

        Returns:
            The parsed :class:`Version`.

        Raises:
            ValidationError: If ``raw`` is not in ``major.minor.patch``
                format with non-negative integer components.
        """
        parts = raw.split(".")
        if len(parts) != 3:
            raise ValidationError(
                'version string must be in "major.minor.patch" format',
                context={"value": raw},
            )
        try:
            major, minor, patch = (int(part) for part in parts)
        except ValueError as exc:
            raise ValidationError(
                'version string must be in "major.minor.patch" format with integer components',
                cause=exc,
                context={"value": raw},
            ) from exc
        return cls(major, minor, patch)

    def __str__(self) -> str:
        """Return the version as ``"major.minor.patch"``."""
        return f"{self.major}.{self.minor}.{self.patch}"
