"""Unit tests for the QuantOS exception hierarchy."""

import pytest

from quant_os.core.exceptions import (
    ConfigurationError,
    DataError,
    InfrastructureError,
    QuantOSError,
    SystemError,
    ValidationError,
)


@pytest.mark.parametrize(
    "exc_class",
    [
        QuantOSError,
        ConfigurationError,
        ValidationError,
        InfrastructureError,
        DataError,
        SystemError,
    ],
)
def test_all_exceptions_are_quant_os_errors(exc_class: type[QuantOSError]) -> None:
    """Every exception in the hierarchy derives from QuantOSError."""
    assert issubclass(exc_class, QuantOSError)


def test_message_only() -> None:
    """An exception created with only a message stores it and defaults cause/context."""
    error = QuantOSError("something went wrong")
    assert error.message == "something went wrong"
    assert error.cause is None
    assert error.context == {}


def test_message_with_cause() -> None:
    """The cause exception is preserved."""
    cause = ValueError("root cause")
    error = QuantOSError("wrapped", cause=cause)
    assert error.cause is cause


def test_message_with_context() -> None:
    """The context dict is copied and preserved."""
    context = {"field": "amount", "value": -1}
    error = QuantOSError("bad value", context=context)
    assert error.context == context
    # Mutating the original dict must not affect the stored context (defensive copy).
    context["field"] = "mutated"
    assert error.context["field"] == "amount"


def test_str_includes_message_only() -> None:
    """String representation with no context/cause shows just the message."""
    error = QuantOSError("plain message")
    assert str(error) == "plain message"


def test_str_includes_context_and_cause() -> None:
    """String representation includes context and cause when present."""
    cause = ValueError("boom")
    error = QuantOSError("failed", cause=cause, context={"k": "v"})
    text = str(error)
    assert "failed" in text
    assert "context=" in text
    assert "cause=" in text


def test_repr() -> None:
    """repr() includes message, cause, and context."""
    error = ValidationError("invalid", context={"field": "x"})
    representation = repr(error)
    assert "ValidationError" in representation
    assert "invalid" in representation
    assert "field" in representation


def test_is_raisable_and_catchable() -> None:
    """Exceptions can be raised and caught as standard Python exceptions."""
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError("bad config")
    assert exc_info.value.message == "bad config"
