# Milestone 2 — Core Infrastructure

**Status:** Complete

## Scope

Build the reusable, generic infrastructure layer under `src/quant_os/core/`
that every future subsystem will depend on. No financial or trading logic
included.

## Delivered

Subpackages under `quant_os.core`:

- **`exceptions`** — `QuantOSError` base class plus `ConfigurationError`,
  `ValidationError`, `InfrastructureError`, `DataError`, `SystemError`.
  Each carries `message`, `cause`, and `context`.
- **`validation`** — `validate_numeric`, `validate_string`,
  `validate_decimal`, `validate_datetime`, `validate_uuid`.
- **`time`** — `utc_now`, `to_iso`, `from_iso`, `validate_timezone_aware`,
  `parse_datetime`, `format_datetime`. All timezone-aware; naive datetimes
  are rejected.
- **`identifiers`** — `TypedId`, a generic immutable UUID wrapper base
  class for future domain-specific identifiers.
- **`types`** — `Money`, `Price`, `Quantity`, `Percentage`, `Probability`,
  `Confidence`, `Version`, `TimeFrame`. Structural validation only, no
  business rules.
- **`config`** — `Environment` and `LogLevel` enums; `Settings` and its
  `DevelopmentSettings` / `TestingSettings` / `ProductionSettings`
  subclasses (via `pydantic-settings`); `get_settings()` cached singleton
  selecting the concrete class from `QUANT_OS_ENVIRONMENT`.
- **`logging`** — `JSONFormatter`, `ColoredConsoleFormatter`,
  `configure_logging()`, `get_logger()`. Stdlib-only; no `print()` used
  anywhere in the codebase.

## Testing

148 tests, 100% statement and branch coverage on `src/quant_os/core`.

## Explicitly Out of Scope

Assets, orders, trades, signals, candles, strategies, risk, broker,
portfolio, AI, or any other finance-domain business logic.
