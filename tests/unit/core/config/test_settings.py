"""Unit tests for the configuration system."""

from collections.abc import Iterator

import pytest

from quant_os.core.config import (
    DevelopmentSettings,
    Environment,
    LogLevel,
    ProductionSettings,
    Settings,
    TestingSettings,
    get_settings,
)
from quant_os.core.config import settings as settings_module
from quant_os.core.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:  # pyright: ignore[reportUnusedFunction]
    """Ensure get_settings()'s cache does not leak state between tests."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestEnvironment:
    def test_members(self) -> None:
        assert Environment.DEVELOPMENT == "development"
        assert Environment.TESTING == "testing"
        assert Environment.PRODUCTION == "production"


class TestLogLevel:
    def test_members(self) -> None:
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"


class TestSettingsDefaults:
    def test_base_settings_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANT_OS_ENVIRONMENT", raising=False)
        settings = Settings()
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.log_level == LogLevel.INFO
        assert settings.debug is False

    def test_development_settings_defaults(self) -> None:
        settings = DevelopmentSettings()
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.log_level == LogLevel.DEBUG
        assert settings.debug is True

    def test_testing_settings_defaults(self) -> None:
        settings = TestingSettings()
        assert settings.environment == Environment.TESTING
        assert settings.log_level == LogLevel.WARNING
        assert settings.debug is True

    def test_production_settings_defaults(self) -> None:
        settings = ProductionSettings()
        assert settings.environment == Environment.PRODUCTION
        assert settings.log_level == LogLevel.INFO
        assert settings.debug is False


class TestResolveSettingsClass:
    """Exercises the private environment-resolution helper via the module namespace.

    Accessed through the module object (rather than imported directly) to
    keep this internal helper out of the package's public API while still
    allowing full coverage of its branches.
    """

    def test_none_defaults_to_development(self) -> None:
        resolver = settings_module._resolve_settings_class  # pyright: ignore[reportPrivateUsage]
        assert resolver(None) is DevelopmentSettings

    def test_development_string(self) -> None:
        resolver = settings_module._resolve_settings_class  # pyright: ignore[reportPrivateUsage]
        assert resolver("development") is DevelopmentSettings

    def test_testing_string(self) -> None:
        resolver = settings_module._resolve_settings_class  # pyright: ignore[reportPrivateUsage]
        assert resolver("testing") is TestingSettings

    def test_production_string(self) -> None:
        resolver = settings_module._resolve_settings_class  # pyright: ignore[reportPrivateUsage]
        assert resolver("production") is ProductionSettings

    def test_unknown_string_raises_configuration_error(self) -> None:
        resolver = settings_module._resolve_settings_class  # pyright: ignore[reportPrivateUsage]
        with pytest.raises(ConfigurationError):
            resolver("not-a-real-environment")


class TestGetSettingsSingleton:
    def test_returns_development_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANT_OS_ENVIRONMENT", raising=False)
        settings = get_settings()
        assert isinstance(settings, DevelopmentSettings)

    def test_is_cached_singleton(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANT_OS_ENVIRONMENT", raising=False)
        first = get_settings()
        second = get_settings()
        assert first is second

    def test_respects_environment_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("QUANT_OS_ENVIRONMENT", "production")
        settings = get_settings()
        assert isinstance(settings, ProductionSettings)

    def test_invalid_environment_variable_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("QUANT_OS_ENVIRONMENT", "not-real")
        with pytest.raises(ConfigurationError):
            get_settings()

    def test_env_var_overrides_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANT_OS_ENVIRONMENT", raising=False)
        monkeypatch.setenv("QUANT_OS_LOG_LEVEL", "ERROR")
        settings = get_settings()
        assert settings.log_level == LogLevel.ERROR

    def test_invalid_field_value_raises_configuration_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("QUANT_OS_ENVIRONMENT", raising=False)
        monkeypatch.setenv("QUANT_OS_LOG_LEVEL", "NOT_A_LEVEL")
        with pytest.raises(ConfigurationError):
            get_settings()
