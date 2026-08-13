"""Unit tests for the Capability enum."""

from quant_os.kernel.capabilities import Capability


def test_all_expected_capabilities_exist() -> None:
    expected = {
        "market_data",
        "news",
        "macro",
        "risk",
        "execution",
        "portfolio",
        "reporting",
        "ai",
    }
    assert {member.value for member in Capability} == expected


def test_capability_is_a_string() -> None:
    assert Capability.NEWS == "news"
