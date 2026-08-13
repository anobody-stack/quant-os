"""Typed, environment-driven application configuration.

Configuration is loaded from environment variables (and an optional
``.env`` file) using ``pydantic-settings``. Values are validated at load
time; invalid configuration raises
:class:`~quant_os.core.exceptions.ConfigurationError` rather than
propagating a raw ``pydantic`` exception, so callers only need to handle
one exception type.

No secrets are hardcoded anywhere in this module.
"""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic import ValidationError as PydanticValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from quant_os.core.config.environment import Environment
from quant_os.core.config.log_level import LogLevel
from quant_os.core.exceptions import ConfigurationError


class Settings(BaseSettings):
    """Base application settings, common to every environment.

    Environment variables are read with the ``QUANT_OS_`` prefix, e.g.
    ``QUANT_OS_LOG_LEVEL=DEBUG`` sets :attr:`log_level`. An optional
    ``.env`` file in the working directory is also read, if present.

    Attributes:
        environment: The runtime environment. Defaults to ``development``.
        log_level: The minimum log level to emit. Defaults to ``INFO``.
        debug: Whether debug mode is enabled. Defaults to ``False``.
    """

    model_config = SettingsConfigDict(
        env_prefix="QUANT_OS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    debug: bool = False


class DevelopmentSettings(Settings):
    """Settings tailored for local development."""

    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.DEBUG
    debug: bool = True


class TestingSettings(Settings):
    """Settings tailored for automated test runs."""

    environment: Environment = Environment.TESTING
    log_level: LogLevel = LogLevel.WARNING
    debug: bool = True


class ProductionSettings(Settings):
    """Settings tailored for production deployment."""

    environment: Environment = Environment.PRODUCTION
    log_level: LogLevel = LogLevel.INFO
    debug: bool = False


_ENVIRONMENT_SETTINGS_MAP: dict[Environment, type[Settings]] = {
    Environment.DEVELOPMENT: DevelopmentSettings,
    Environment.TESTING: TestingSettings,
    Environment.PRODUCTION: ProductionSettings,
}


def _resolve_settings_class(environment_value: str | None) -> type[Settings]:
    """Resolve the concrete settings class for a raw environment string.

    Args:
        environment_value: The raw value of the ``QUANT_OS_ENVIRONMENT``
            environment variable, or ``None`` if unset.

    Returns:
        The settings class corresponding to the resolved environment.
        Defaults to :class:`DevelopmentSettings` when unset.

    Raises:
        ConfigurationError: If ``environment_value`` does not correspond to
            a known :class:`~quant_os.core.config.environment.Environment`.
    """
    if environment_value is None:
        return DevelopmentSettings
    try:
        environment = Environment(environment_value)
    except ValueError as exc:
        valid = ", ".join(member.value for member in Environment)
        raise ConfigurationError(
            f"Unknown environment {environment_value!r}; expected one of: {valid}",
            cause=exc,
            context={"environment_value": environment_value},
        ) from exc
    return _ENVIRONMENT_SETTINGS_MAP[environment]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide singleton :class:`Settings` instance.

    The concrete settings class is selected based on the
    ``QUANT_OS_ENVIRONMENT`` environment variable (``development``,
    ``testing``, or ``production``); it defaults to
    :class:`DevelopmentSettings` when unset. The result is cached for the
    lifetime of the process — call :func:`get_settings.cache_clear` to
    force a reload (primarily useful in tests).

    Returns:
        The loaded, validated settings instance.

    Raises:
        ConfigurationError: If the environment variable names an unknown
            environment, or if any configuration value fails validation.
    """
    settings_class = _resolve_settings_class(os.environ.get("QUANT_OS_ENVIRONMENT"))
    try:
        return settings_class()
    except PydanticValidationError as exc:
        raise ConfigurationError(
            "Application configuration failed validation",
            cause=exc,
            context={"errors": exc.errors()},
        ) from exc
