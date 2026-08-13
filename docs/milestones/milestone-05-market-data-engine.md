# Milestone 5 — Market Data Engine

**Status:** Complete

## Scope

Build the complete Market Data Engine as the single source of truth for
market prices, fully integrated with the Event System (Milestone 3) and
Application Kernel (Milestone 4). Only mock (synthetic) providers — no
real HTTP requests, no databases, no trading/strategy/risk logic.

## Architectural Decisions (flagged upfront, not objected to)

- Restructured `market/` from Milestone 3's flat `provider.py`/
  `repository.py` into the full subpackage layout specified:
  `models/`, `interfaces/`, `providers/`, `repositories/`, `cache/`,
  `validation/`, `subscriptions/`, `events/`, `services/`.
- Extended `EventType` (`quant_os.events.enums`, Milestone 3) with 8 new
  market-specific members, required for event-system integration.
- `market/models/timeframe.py::TimeFrame` kept distinct from
  `core.types.TimeFrame` — the market timeframe needs `TICK` (no fixed
  duration) and `MN1` (variable-length calendar month), neither of which
  fits `core`'s fixed-seconds design.
- Tick events reuse Milestone 3's `MarketTickReceived` rather than
  duplicating it as a new `TickReceived` class.

## Delivered

### `quant_os.market.models`
`Symbol`, `AssetClass`, `TimeFrame`, `PricePrecision`, `Exchange`,
`MarketSession`, `MarketStatus`, `Market`, `Asset`, `MarketMetadata`,
`Tick`, `Quote`, `OHLCVCandle`, `OrderBookLevel`/`OrderBookSnapshot`.
All immutable (frozen pydantic models). Validation includes OHLC
consistency, bid≤ask spread, and timezone-aware timestamps throughout.

### `quant_os.market.interfaces`
Contracts only: `MarketDataProvider`, `HistoricalDataProvider`,
`StreamingProvider`, `QuoteProvider`, `MetadataProvider` (providers);
`TickRepository`, `QuoteRepository`, `CandleRepository`,
`MetadataRepository`, `MarketRepository` (composite facade, exposed as
read-only properties for correct structural typing).

### `quant_os.market.providers`
`MockMarketDataProvider` — implements every provider interface with a
deterministic (seeded), Decimal-precise random walk. No network access.
Supports the 4 initial assets via `quant_os.market.assets`.

### `quant_os.market.repositories`
In-memory implementations of all 5 repository interfaces, bounded
history (deque-based) for ticks and candles.

### `quant_os.market.cache`
`MarketCache` — TTL-based cache for latest tick, latest quote, windowed
candles (configurable history size), and metadata, with `invalidate()`
and `clear()`.

### `quant_os.market.validation`
`validate_tick` (future-timestamp + duplicate detection),
`validate_quote` (future-timestamp), `validate_precision` (tick-size
conformance).

### `quant_os.market.subscriptions`
`SubscriptionManager`/`SubscriptionFilter` — symbol/timeframe-filtered
subscriptions layered on the shared `EventBus`, avoiding the need for
every consumer to filter raw event payloads itself.

### `quant_os.market.events`
`QuoteUpdated`, `CandleOpened`, `CandleClosed`, `MarketOpened`,
`MarketClosed`, `ProviderConnected`, `ProviderDisconnected`,
`HistoricalDataLoaded`.

### `quant_os.market.services`
`MarketService` — the central entry point: `connect`/`disconnect`,
`ingest_tick`/`ingest_quote`/`ingest_candle` (validate → store → cache →
publish), `get_latest_price`/`get_latest_quote` (cache-first reads),
`get_historical_candles`, `fetch_and_ingest_quote`.

`MarketModule` — the Kernel `Module` wrapper: advertises
`Capability.MARKET_DATA`, connects/disconnects the provider on
start/stop, starts/stops the `SubscriptionManager`, and reports health
(`HEALTHY` when the provider is connected, `UNAVAILABLE` otherwise).

### `quant_os.market.assets`
The registry of the 4 initially supported assets (Gold/XAUUSD, WTI Crude
Oil/WTIUSD, Brent Crude Oil/BCOUSD, EUR/USD/EURUSD), each with realistic
precision/tick-size. Adding a future asset is one registry entry.

## Testing

444 tests total across the repository (296 new for Milestone 5).
~96.4% coverage on `quant_os.market` (target: ≥95%); 97% overall
repository coverage. Remaining gaps are unreachable `Protocol` interface
stub bodies (same pattern as prior milestones).

## Explicitly Out of Scope

Broker APIs, trading, orders, execution, strategies, portfolio, risk,
indicators, technical analysis, machine learning, AI, news, economic
calendar, databases, external APIs, or real HTTP requests.
