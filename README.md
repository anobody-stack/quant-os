# QuantOS

Institutional-grade, modular financial operating system for research, analysis, risk management, and automated trading.

## Overview

QuantOS is a long-horizon software platform designed to support the full lifecycle of quantitative and discretionary trading operations: market data ingestion, research, risk management, portfolio accounting, reporting, and execution. It is built to be extensible across asset classes, starting with:

- **Gold**
- **Crude Oil**

The system is designed for correctness, auditability, and maintainability first, in line with the standards expected of institutional financial software.

## Vision

QuantOS aims to become a unified operating layer for systematic and discretionary trading desks — replacing fragmented spreadsheets, scripts, and disconnected tools with a single, well-tested, well-documented codebase that can scale from a single asset to a full multi-asset trading operation.

## Architecture Overview

QuantOS is organized as a modular monolith, with clear separation of concerns across functional domains. Each module under `quant_os/` owns a distinct responsibility and is designed to be independently testable.

At this stage (Milestones 1–5 complete), the core infrastructure, event
system, application kernel, and Market Data Engine are implemented and
tested. The structure below shows the boundaries the remaining milestones
will fill in.

## Repository Structure

```
quant-os/
│
├── src/
│   └── quant_os/
│       ├── core/             # Core infrastructure: config, logging, exceptions, time, identifiers, types, validation
│       ├── kernel/           # Application kernel: DI container, registry, modules, lifecycle, health, bootstrap
│       ├── events/           # Event system: Event, EventBus, AsyncEventBus, domain events
│       ├── market/           # Market Data Engine: models, interfaces, mock provider, repositories, cache, service
│       ├── data/             # Providers, ingestion, persistence, normalization, storage (placeholder)
│       ├── news/             # News domain (provider/repository interfaces)
│       ├── macro/            # Macro/economic calendar domain (provider/repository interfaces)
│       ├── trading/          # Order management and execution (legacy placeholder)
│       ├── strategy/         # Strategy agent domain (placeholder)
│       ├── execution/        # Execution domain (placeholder)
│       ├── risk/             # Risk measurement, limits, exposure management
│       ├── reporting/        # Report generation and output formatting
│       ├── ai/               # AI/ML-driven research and decision support
│       ├── portfolio/        # Portfolio construction, tracking, accounting
│       ├── infrastructure/   # Integrations: brokers, data vendors, storage, scheduler
│       └── utils/            # Cross-cutting, dependency-free utilities
│
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
│
├── docs/
│   ├── architecture/         # Architecture documentation
│   ├── decisions/            # Architecture Decision Records (ADRs)
│   ├── milestones/           # Milestone specifications and records
│   └── PROJECT_BIBLE.md      # Mission, principles, and standards
│
├── configs/                  # Configuration files
├── scripts/                  # Operational and developer scripts
├── notebooks/                # Research notebooks
├── data/
│   ├── raw/                  # Raw, unmodified data
│   ├── processed/            # Cleaned/derived data
│   └── cache/                # Ephemeral cached data
│
└── .github/workflows/        # CI pipelines
```

## Installation

QuantOS uses [`uv`](https://docs.astral.sh/uv/) for dependency and environment management, and requires Python 3.12 or later.

```bash
# Clone the repository
git clone <repository-url>
cd quant-os

# Install dependencies (creates a virtual environment automatically)
uv sync
```

## Development Setup

Copy the example environment file and fill in any local configuration:

```bash
cp .env.example .env
```

No secrets are committed to this repository. `.env` is git-ignored.

## Running Tests

```bash
uv run pytest
```

Test coverage is measured automatically via `pytest-cov` and reported on every run.

## Code Quality Commands

QuantOS enforces strict linting, formatting, and type-checking standards.

```bash
# Lint
uv run ruff check .

# Format check
uv run black --check .

# Format (apply)
uv run black .

# Type check
uv run pyright

# Full test suite
uv run pytest
```

All four checks must pass before any change is merged.

## Event System

QuantOS is event-driven at its core. Every subsystem — market data, news,
macro/economic calendar, strategy agents, risk, portfolio, execution, AI,
and reporting — communicates through a single, generic, asynchronous
`EventBus` rather than calling one another directly.

### Core concepts

- **`Event`** (`quant_os.events.base`) — the abstract base every domain
  event derives from. Frozen (immutable) and carries an `EventMetadata`
  envelope plus an `event_type` discriminator.
- **`EventMetadata`** — envelope information common to all events:
  `event_id`, UTC `timestamp`, `source`, `priority`, and an optional
  `correlation_id` for tracing causally related events.
- **`EventType`** / **`EventPriority`** — the classification vocabulary.
  `EventType` identifies what happened; `EventPriority` (an ordered
  `IntEnum`) identifies how urgently it should be handled.
- **Domain events** (`quant_os.events.domain_events`) — pure data models,
  no behavior: `NewsReceived`, `EconomicEventReceived`,
  `MarketTickReceived`, `SignalGenerated`, `RiskAlert`, `OrderCreated`,
  `OrderFilled`, `PositionOpened`, `PositionClosed`, `PortfolioUpdated`.

### EventBus

- **`EventBus`** (`quant_os.events.bus`) — the abstract interface:
  `publish`, `subscribe`, `unsubscribe`, `add_middleware`.
- **`AsyncEventBus`** (`quant_os.events.async_bus`) — the in-memory,
  asyncio-native implementation. Subscribers for a given event type are
  invoked concurrently; middleware wraps the entire dispatch chain,
  outermost-first.

No external broker or message queue is used — this is a pure in-process
abstraction. Handler failures are aggregated and raised as
`InfrastructureError` rather than silently swallowed; other subscribers
still run even if one fails.

#### Example

```python
import asyncio
from quant_os.events import AsyncEventBus, EventMetadata, EventType, RiskAlert
from quant_os.events.enums import EventPriority


async def main() -> None:
    bus = AsyncEventBus()

    async def on_risk_alert(event: RiskAlert) -> None:
        print(f"Risk alert: {event.message} ({event.severity.name})")

    subscription_id = await bus.subscribe(EventType.RISK_ALERT, on_risk_alert)

    await bus.publish(
        RiskAlert(
            metadata=EventMetadata(source="risk.drawdown_monitor"),
            message="Max drawdown threshold breached",
            severity=EventPriority.CRITICAL,
        )
    )

    await bus.unsubscribe(subscription_id)


asyncio.run(main())
```

#### Middleware

```python
from quant_os.events.base import Event
from quant_os.events.bus import EventHandler


async def logging_middleware(event: Event, next_handler: EventHandler) -> None:
    print(f"dispatching {event.event_type}")
    await next_handler(event)
    print(f"dispatched {event.event_type}")


bus.add_middleware(logging_middleware)
```

## Application Kernel

The kernel (`quant_os.kernel`) is the operating-system layer every future
module plugs into. It owns dependency injection, service registration,
module lifecycle, health monitoring, configuration binding, and
application bootstrapping. It contains no domain-specific logic.

### Dependency Injection

`Container` (`quant_os.kernel.container`) is a reflection-based DI
container: a registered implementation's `__init__` type hints are
inspected to resolve its dependencies automatically (constructor
injection).

```
┌─────────────────────────────────────────────────────────────┐
│                          Container                           │
│                                                               │
│   register_singleton(EventBus, AsyncEventBus)                │
│   register_transient(ReportGenerator, ReportGenerator)        │
│                                                               │
│   resolve(ReportGenerator)                                   │
│        │                                                     │
│        ▼                                                     │
│   inspect ReportGenerator.__init__ type hints                │
│        │                                                     │
│        ▼                                                     │
│   ┌─────────────────────┐                                   │
│   │ needs: EventBus      │──▶ resolve(EventBus)              │
│   │ needs: Settings       │──▶ resolve(Settings)              │
│   └─────────────────────┘        (singleton, cached)         │
│        │                                                     │
│        ▼                                                     │
│   ReportGenerator(event_bus=..., settings=...)                │
└─────────────────────────────────────────────────────────────┘
```

Supported lifetimes: `SINGLETON` (one instance for the container's
lifetime), `TRANSIENT` (a new instance every resolution), `SCOPED` (one
instance per `Scope`, via `container.create_scope()`). Circular
dependencies are detected at resolution time (or proactively via
`container.validate_graph()`) and raise `CircularDependencyError` with the
full dependency chain.

`ServiceRegistry` (`quant_os.kernel.registry`) wraps a `Container` and
additionally tracks `ServiceMetadata` (lifetime, description, registering
module, registration time) for introspection — `list_services()`,
`exists()`, `remove()`, `override()`.

### Module System and Lifecycle

Every module implements `Module` (`quant_os.kernel.module`): a `metadata`
property (`ModuleMetadata`: name, version, description, dependencies,
capabilities) plus lifecycle hooks (`on_initialize`, `on_start`,
`on_stop`, `on_dispose`, `check_health`), all defaulting to no-ops except
`metadata` itself.

```
   CREATED
      │ INITIALIZING
      ▼
  INITIALIZING ──(failure)──▶ FAILED ──▶ INITIALIZING (restart)
      │ INITIALIZED                        │
      ▼                                    ▼
  INITIALIZED                          SHUTTING_DOWN
      │ STARTING                           │
      ▼                                    ▼
   STARTING ──(failure)──▶ FAILED       DISPOSED
      │ READY
      ▼
    READY ──(failure)──▶ FAILED
      │ STOPPING
      ▼
   STOPPING ──(failure)──▶ FAILED
      │ STOPPED
      ▼
   STOPPED ──(restart)──▶ STARTING
      │ SHUTTING_DOWN
      ▼
 SHUTTING_DOWN ──(failure)──▶ FAILED
      │ DISPOSED
      ▼
   DISPOSED  (terminal)
```

`LifecycleManager` (`quant_os.kernel.lifecycle`) tracks each module's
state independently and rejects any transition not shown above, raising
`ModuleLifecycleError`.

`Application` (`quant_os.kernel.application`) orchestrates modules:
`register_module()` validates declared dependencies are already
registered; `initialize()`/`start()` run in dependency order (topological
sort, cycle-checked); `shutdown()` runs in reverse order and is
best-effort — one module failing to stop doesn't block the others, and
all failures are aggregated into a single `ShutdownError`.

#### Example: registering and running a module

```python
from quant_os.core.types import Version
from quant_os.kernel import Application, Module, ModuleMetadata, Capability


class NewsModule(Module):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="news",
            version=Version(1, 0, 0),
            description="Financial news ingestion",
            capabilities=(Capability.NEWS,),
        )

    async def on_start(self) -> None: ...  # begin polling/streaming


app = Application()
app.register_module(NewsModule())
await app.initialize()
await app.start()
...
await app.shutdown()
```

### Configuration Binding

`build_container()` (`quant_os.kernel.bootstrap`) resolves
`Settings` once and registers the concrete instance as a singleton — no
module should call `get_settings()` directly. A module simply declares
`Settings` as a constructor parameter and the container supplies it:

```python
class NewsModule(Module):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    ...
```

`build_container()` also registers `EventBus` (backed by `AsyncEventBus`),
`LifecycleManager`, and `HealthAggregator` as singletons, so modules
resolve all of these the same way — via constructor injection, never by
reaching into a global.

### Health Monitoring

Modules report `HealthStatus`: `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, or
`UNKNOWN` (the default). `Application.run_health_checks()` runs every
registered module's `check_health()` concurrently via `HealthAggregator`
and returns a `HealthReport` whose `overall_status` is the worst status
present — a check that raises is reported as `UNAVAILABLE` rather than
crashing the whole report.

```python
report = await app.run_health_checks()
print(report.overall_status)  # e.g. HealthStatus.DEGRADED
print(report.results["news"].status)  # per-module detail
```

### Capabilities

Modules advertise `Capability` values (`MARKET_DATA`, `NEWS`, `MACRO`,
`RISK`, `EXECUTION`, `PORTFOLIO`, `REPORTING`, `AI`) in their metadata
instead of exposing implementation types — other code can discover "does
some registered module do X" without depending on a concrete class.

### Plugin Foundation

`Plugin`, `PluginMetadata`, and `PluginManager` (`quant_os.kernel.plugin`)
define the shape future plugin infrastructure will conform to. No
loading, discovery, or sandboxing mechanism exists yet — these are
interfaces only.

## Market Data Engine (Milestone 5)

`quant_os.market` is the single source of truth for market prices. No
other module accesses a provider directly — every subsystem consumes
market data through `MarketService`.

**Supported assets:** Gold (XAUUSD), WTI Crude Oil, Brent Crude Oil,
EUR/USD (`quant_os.market.assets.SUPPORTED_ASSETS`). Adding a new asset
is one registry entry — no structural change.

### Data flow

```
MockMarketDataProvider (synthetic, seeded random walk)
        │  Tick / Quote / OHLCVCandle (QuantOS models only)
        ▼
   MarketService.ingest_*()
        │  validate (future timestamp, duplicates, OHLC/spread
        │  already enforced by the models themselves)
        ▼
   InMemoryMarketRepository (persist)  +  MarketCache (TTL cache)
        │
        ▼
   EventBus.publish(MarketTickReceived / QuoteUpdated / CandleClosed / ...)
        │
        ▼
   SubscriptionManager ──▶ filtered listeners (by symbol / timeframe)
```

### Event flow

```
MarketModule.on_start() ──▶ MarketService.connect() ──▶ ProviderConnected
                        └─▶ SubscriptionManager.start() (subscribes to
                             MARKET_TICK_RECEIVED, QUOTE_UPDATED,
                             CANDLE_CLOSED on the shared EventBus)

ingest_tick()   ──▶ MarketTickReceived
ingest_quote()  ──▶ QuoteUpdated
ingest_candle() ──▶ CandleClosed
get_historical_candles() ──▶ HistoricalDataLoaded

MarketModule.on_stop() ──▶ SubscriptionManager.stop()
                       └─▶ MarketService.disconnect() ──▶ ProviderDisconnected
```

### Public API example

```python
from quant_os.market import MarketModule, MarketService
from quant_os.market.assets import get_supported_asset
from quant_os.market.cache import MarketCache
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.timeframe import TimeFrame
from quant_os.market.providers.mock_provider import MockMarketDataProvider
from quant_os.market.repositories import InMemoryMarketRepository
from quant_os.events import AsyncEventBus

service = MarketService(
    MockMarketDataProvider(), InMemoryMarketRepository(), MarketCache(), AsyncEventBus()
)
await service.connect()
quote = await service.fetch_and_ingest_quote(Symbol(code="XAUUSD"))
candles = await service.get_historical_candles(
    Symbol(code="XAUUSD"),
    TimeFrame.M1,
    start=...,
    end=...,
)
```

Register with the Kernel via `MarketModule` (see `Application` above) —
`app.register_module(MarketModule(provider, repository, cache, event_bus))`.

Architecture: `models/` (immutable domain models) → `interfaces/`
(Protocol contracts) → `providers/` (mock only, this milestone) →
`repositories/` (in-memory) → `cache/` (TTL) → `validation/` →
`subscriptions/` (filtered pub/sub over the EventBus) → `events/`
(market-specific EventBus events) → `services/` (`MarketService` entry
point + `MarketModule` Kernel wrapper).

## Domain Interfaces (Milestone 3)

The following domains currently expose **interfaces only** — no concrete
implementation, storage, or scheduling logic exists yet. This keeps
provider- and backend-specific detail out of the domain layer from day
one.

| Domain | Provider interface | Repository interface |
|---|---|---|
| News | `quant_os.news.provider.NewsProvider` | `quant_os.news.repository.NewsRepository` |
| Macro/calendar | `quant_os.macro.provider.MacroProvider` | `quant_os.macro.repository.MacroRepository` |

All are `typing.Protocol` classes (structural typing, `@runtime_checkable`)
rather than ABCs — any object with matching async methods satisfies the
interface without explicit inheritance.

`quant_os.infrastructure.scheduler.Scheduler` is a similar interface for
future polling/streaming/calendar-driven scheduling (`start`, `stop`,
`schedule`, `cancel`) — no cron, timer, or APScheduler logic is
implemented yet.

## Future Roadmap Summary

Completed:

- Repository foundation, tooling, and standards (Milestone 1)
- Core infrastructure: config, logging, exceptions, time, identifiers,
  value types, validation (Milestone 2)
- Event system: `Event`/`EventMetadata`/`EventBus`/`AsyncEventBus`,
  domain event definitions, and provider/repository/scheduler interfaces
  for market data, news, and macro (Milestone 3)
- Application Kernel: dependency injection container, service registry,
  module system and lifecycle management, health monitoring, capability
  system, configuration binding, and application bootstrap (Milestone 4)
- Market Data Engine: domain models, provider/repository interfaces, a
  synthetic mock provider, in-memory repositories, TTL cache, validation,
  asset/timeframe-filtered subscriptions, market-specific events, and the
  `MarketService`/`MarketModule` entry points, fully integrated with the
  Event System and Kernel (Milestone 5)

Subsequent milestones will incrementally introduce:

- Concrete provider implementations (market data feeds, news sources,
  economic calendars)
- Persistent repository implementations
- Concrete scheduler implementation
- News/macro classification, asset mapping, and importance/confidence
  scoring
- Risk measurement and limit enforcement
- Portfolio accounting and tracking
- Reporting pipelines
- Trading execution and broker integrations
- AI-assisted research components

Each milestone will be documented under `docs/milestones/` prior to
implementation.

## License

MIT — see [LICENSE](./LICENSE).
