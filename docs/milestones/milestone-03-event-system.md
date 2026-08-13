# Milestone 3 — Event System

**Status:** Complete

## Scope

Build only the event system and interface layer: the `EventBus`
abstraction, domain event definitions, and provider/repository/scheduler
interfaces. No implementations, storage, ingestion, or business logic.

## Architectural Decisions (per explicit CTO direction)

- The event bus is new core infrastructure — no prior event system or
  market data engine existed in this repository.
- Project structure extended with new top-level packages: `events`,
  `market`, `news`, `macro`, `strategy`, `execution`. News and macro are
  first-class domains, not subpackages of `data`.
- `data/` is reserved for providers, ingestion, persistence,
  normalization, and storage (unchanged from Milestone 1's definition).
- The legacy `trading/` package (Milestone 1) was left untouched — it is
  not part of the new official layout, but removing it was not requested
  and would be destructive; flagged for a future decision.
- `strategy/` and `execution/` are placeholder packages only (mandated by
  the new layout, but out of this milestone's coded scope).
- `Scheduler` was placed in `infrastructure/` as generic technical infra,
  not tied to any single domain.

## Delivered

### `quant_os.events`

- `enums.py` — `EventType` (`StrEnum`), `EventPriority` (`IntEnum`)
- `metadata.py` — `EventMetadata` (frozen pydantic model; UTC-validated
  timestamp; non-blank source)
- `base.py` — abstract `Event` base (frozen; blocks direct instantiation)
- `domain_events.py` — 10 concrete events, pure data models: `NewsReceived`,
  `EconomicEventReceived`, `MarketTickReceived`, `SignalGenerated`,
  `RiskAlert`, `OrderCreated`, `OrderFilled`, `PositionOpened`,
  `PositionClosed`, `PortfolioUpdated`
- `bus.py` — `EventBus` Protocol (publish/subscribe/unsubscribe/
  add_middleware), `SubscriptionId`, `EventHandler`/`Middleware` type
  aliases
- `async_bus.py` — `AsyncEventBus`: in-memory, asyncio-native
  implementation with concurrent fan-out per event type, ordered
  middleware chaining, and aggregated error reporting via
  `InfrastructureError`

### Interfaces only (no implementations)

- `market/provider.py` — `MarketDataProvider`
- `market/repository.py` — `MarketRepository`
- `news/provider.py` — `NewsProvider`
- `news/repository.py` — `NewsRepository`
- `macro/provider.py` — `MacroProvider`
- `macro/repository.py` — `MacroRepository`
- `infrastructure/scheduler.py` — `Scheduler`, `ScheduleHandle`

### Supporting change

- `core.identifiers.TypedId.generate()`/`.from_string()` now return
  `Self` instead of `TypedId`, required for subclass identifiers
  (`SubscriptionId`, `ScheduleHandle`) to type-check correctly. Behavior
  unchanged; Milestone 2 tests re-verified passing.

## Testing

199 tests total (51 new for Milestone 3). 97% overall coverage; the only
uncovered lines are unreachable `...` bodies of `Protocol` interface stubs.

## Explicitly Out of Scope

Concrete providers, repository implementations, scheduler implementation,
classification, asset/country mapping, importance/confidence scoring,
deduplication, timeline service, search engine, caching, ingestion, or any
other business/financial logic.
