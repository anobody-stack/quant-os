"""Smoke tests for the QuantOS repository foundation.

These tests verify the package skeleton is importable and correctly
versioned. They intentionally contain no business logic.
"""

import importlib

import quant_os

EXPECTED_SUBPACKAGES = (
    "ai",
    "core",
    "data",
    "events",
    "execution",
    "infrastructure",
    "kernel",
    "macro",
    "market",
    "news",
    "portfolio",
    "reporting",
    "risk",
    "strategy",
    "trading",
    "utils",
)


def test_quant_os_package_has_version() -> None:
    """The top-level package exposes a semantic version string."""
    assert isinstance(quant_os.__version__, str)
    assert quant_os.__version__ == "0.1.0"


def test_all_subpackages_are_importable() -> None:
    """Every declared subpackage under quant_os imports without error."""
    for subpackage in EXPECTED_SUBPACKAGES:
        module = importlib.import_module(f"quant_os.{subpackage}")
        assert module.__doc__ is not None, f"quant_os.{subpackage} must have a docstring"
