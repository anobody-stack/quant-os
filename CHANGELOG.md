# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Market Data Engine (Milestone 5): `quant_os.market` — the single
  source of truth for market prices, fully integrated with the Event
  System (Milestone 3) and Kernel (Milestone 4).
  - **Models**: `Symbol`, `AssetClass`, `TimeFrame` (market-specific),
    `PricePrecision`, `Exchange`, `MarketSession`, `MarketStatus`,
    `Market`, `Asset`, `MarketMetadata`, `Tick`, `Quote`, `OHLCVCandle`,
    `OrderBookSnapshot`/`OrderBookLevel` — all immutable, validated
    (OHLC consistency, bid≤ask spread, timezone-aware timestamps).
  - **Interfaces** (contracts only): `MarketDataProvider`,
    `HistoricalDataProvider`, `StreamingProvider`, `QuoteProvider`,
    `MetadataProvider`, `TickRepository`, `QuoteRepository`,
    `CandleRepository`, `MetadataRepository`, `MarketRepository`.
  - **Providers**: `MockMarketDataProvider` — deterministic, seeded
    synthetic data generator for the 4 supported assets (Gold, WTI,
    Brent, EUR/USD); no network access.
  - **Repositories**: in-memory implementations of all 5 repository
    interfaces.
  - **Cache**: `MarketCache` — TTL-based cache for latest tick/quote,
    windowed candles, and metadata.
  - **Validation**: `validate_tick`, `validate_quote`,
    `validate_precision` (future-timestamp rejection, duplicate
    detection, tick-size conformance).
  - **Subscriptions**: `SubscriptionManager`/`SubscriptionFilter` —
    symbol/timeframe-filtered subscriptions layered on the EventBus.
  - **Events**: `QuoteUpdated`, `CandleOpened`, `CandleClosed`,
    `MarketOpened`, `MarketClosed`, `ProviderConnected`,
    `ProviderDisconnected`, `HistoricalDataLoaded` (ticks reuse M3's
    `MarketTickReceived`).
  - **Services**: `MarketService` (central entry point: ingest, validate,
    store, cache, publish, serve) and `MarketModule` (Kernel `Module`
    integration: capability advertisement, connect/disconnect lifecycle,
    health reporting).
  - `EventType` (M3) extended with 8 new market-specific members.

### Changed

- `market/` restructured from Milestone 3's flat `provider.py`/
  `repository.py` into the full subpackage layout
  (`models/interfaces/providers/repositories/cache/validation/
  subscriptions/events/services`), per explicit direction. The obsolete
  M3 interface test file was removed and superseded by the full M5
  interface test suite.
- `MarketRepository` Protocol's sub-repository accessors changed from
  plain attributes to read-only properties, required for structural
  typing to correctly recognize compatible implementations under
  pyright strict mode.

- Application Kernel (Milestone 4): `quant_os.kernel` — dependency
  injection container (`Container`, `Scope`) with singleton/transient/
  scoped lifetimes, reflection-based constructor injection, factory
  registration, circular-dependency detection, and dependency-graph
  validation; `ServiceRegistry` (metadata-tracking catalog); `Module`/
  `ModuleMetadata` base abstraction; `LifecycleManager`/`ModuleState`
  (enforced state-transition table with restart support); `HealthStatus`/
  `HealthCheckResult`/`HealthReport`/`HealthAggregator`; `Capability` enum;
  `Plugin`/`PluginMetadata`/`PluginManager` (interfaces only, no loading);
  `build_container()` (configuration binding: `Settings`, `EventBus`,
  `LifecycleManager`, `HealthAggregator` registered as singletons);
  `Application` (module registration, dependency-ordered
  initialize/start, concurrent health checks, best-effort aggregated
  shutdown).

### Fixed

- Several `logger.*(..., extra={"module": ...})` calls in
  `quant_os.kernel` collided with Python's stdlib `LogRecord.module`
  reserved attribute. This was latent (masked by default log level
  filtering below ERROR) but would have crashed at ERROR level in
  production. Renamed to `module_name` throughout; verified no other
  reserved-attribute collisions exist in the codebase.

- Event system (Milestone 3): `quant_os.events` — `Event`, `EventMetadata`,
  `EventType`, `EventPriority`, `EventBus` interface, `AsyncEventBus`
  in-memory implementation (publish/subscribe/unsubscribe/middleware), and
  10 concrete domain event definitions (`NewsReceived`,
  `EconomicEventReceived`, `MarketTickReceived`, `SignalGenerated`,
  `RiskAlert`, `OrderCreated`, `OrderFilled`, `PositionOpened`,
  `PositionClosed`, `PortfolioUpdated`).
- New top-level packages: `events`, `market`, `news`, `macro`, `strategy`
  (placeholder), `execution` (placeholder).
- Provider interfaces (no implementations): `MarketDataProvider`,
  `NewsProvider`, `MacroProvider`.
- Repository interfaces (no implementations): `MarketRepository`,
  `NewsRepository`, `MacroRepository`.
- Scheduler interface (no implementation):
  `quant_os.infrastructure.scheduler.Scheduler`.
- `pytest-asyncio` added as a dev dependency; pytest configured with
  `asyncio_mode = "strict"`.

### Changed

- `quant_os.core.identifiers.TypedId.generate()` and `.from_string()` now
  return `Self` instead of `TypedId`, so identifier subclasses (e.g.
  `SubscriptionId`, `ScheduleHandle`) type-check correctly under pyright
  strict mode. Behavior is unchanged; this is a type-annotation fix only.

- Core infrastructure layer (Milestone 2): `quant_os.core` now provides
  `config`, `logging`, `exceptions`, `time`, `identifiers`, `types`, and
  `validation` subpackages — reusable, domain-agnostic infrastructure with
  100% test coverage. No trading, asset, or other financial logic included.

## [0.1.0] - 2026-08-01

### Added

- Repository foundation established (Milestone 1).
- `quant_os` package skeleton with placeholder subpackages: `core`, `data`,
  `trading`, `risk`, `reporting`, `ai`, `portfolio`, `infrastructure`, `utils`.
- Test directory structure (`tests/unit`, `tests/integration`).
- Documentation scaffolding (`docs/architecture`, `docs/decisions`,
  `docs/milestones`, `PROJECT_BIBLE.md`).
- Project tooling configuration: `uv`, `ruff`, `black`, `pyright`, `pytest`,
  `pytest-cov`.
- CI pipeline (`.github/workflows/ci.yml`) running lint, format, type, and
  test checks.
- `README.md`, `LICENSE` (MIT), `.gitignore`, `.env.example`.

No business or trading logic included in this release.
