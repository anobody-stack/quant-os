"""Macro domain: providers and repositories for economic/calendar events.

This package currently exposes interfaces only
(:class:`~quant_os.macro.provider.MacroProvider`,
:class:`~quant_os.macro.repository.MacroRepository`). Concrete
implementations are reserved for a later milestone.
"""

from quant_os.macro.provider import MacroProvider
from quant_os.macro.repository import MacroRepository

__all__ = ["MacroProvider", "MacroRepository"]
