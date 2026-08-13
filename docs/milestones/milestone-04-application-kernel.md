# Milestone 4 — Application Kernel

**Status:** Complete

## Scope

Build the QuantOS Application Kernel: dependency injection, service
registration, module registration, lifecycle management, health
monitoring, configuration binding, and application bootstrapping. No
domain-specific logic (market data, news, trading, risk, portfolio,
execution, AI, databases, HTTP, GUI).

## Delivered

### `quant_os.kernel`

- **`exceptions.py`** — `KernelError` (extends
  `core.exceptions.InfrastructureError`) plus `ServiceNotRegisteredError`,
  `DuplicateRegistrationError`, `CircularDependencyError`,
  `InvalidRegistrationError`, `ModuleLifecycleError`,
  `ModuleDependencyError`, `StartupError`, `ShutdownError`,
  `HealthCheckError`.
- **`service.py`** — `ServiceLifetime` (`SINGLETON`/`TRANSIENT`/`SCOPED`),
  `ServiceDescriptor`.
- **`container.py`** — `Container`: reflection-based constructor
  injection (inspects `__init__` type hints), all three lifetimes,
  `Scope` (context manager), factory registration, service replacement,
  circular-dependency detection at resolution time, and proactive
  `validate_graph()`.
- **`registry.py`** — `ServiceRegistry`: metadata-tracking facade over
  `Container` (`ServiceMetadata`: lifetime, description, registered_by,
  registered_at); `list_services()`, `exists()`, `remove()`, `override()`.
- **`capabilities.py`** — `Capability` enum: `MARKET_DATA`, `NEWS`,
  `MACRO`, `RISK`, `EXECUTION`, `PORTFOLIO`, `REPORTING`, `AI`.
- **`module.py`** — `Module` ABC (abstract `metadata` property; no-op
  default lifecycle hooks `on_initialize`/`on_start`/`on_stop`/
  `on_dispose`; default `check_health` returns `UNKNOWN`), `ModuleMetadata`
  (name, version, description, dependencies, capabilities).
- **`lifecycle.py`** — `ModuleState` (10 states per spec: CREATED,
  INITIALIZING, INITIALIZED, STARTING, READY, STOPPING, STOPPED,
  SHUTTING_DOWN, DISPOSED, FAILED) and `LifecycleManager` enforcing a
  strict transition table, including restart paths
  (`STOPPED → STARTING`, `FAILED → INITIALIZING`).
- **`health.py`** — `HealthStatus` (`HEALTHY`/`DEGRADED`/`UNAVAILABLE`/
  `UNKNOWN`), `HealthCheckResult`, `HealthCheckable` Protocol,
  `HealthReport` (worst-of aggregation via `overall_status`),
  `HealthAggregator` (concurrent checks; a raising check is reported as
  `UNAVAILABLE`, never propagates).
- **`plugin.py`** — `Plugin` (ABC), `PluginMetadata`, `PluginManager`
  (Protocol). Interfaces only — no loading, discovery, or sandboxing.
- **`bootstrap.py`** — `build_container()`: configuration binding.
  Resolves `Settings` once and registers the concrete instance as a
  singleton; also registers `EventBus` (backed by `AsyncEventBus`),
  `LifecycleManager`, `HealthAggregator`.
- **`application.py`** — `Application`: `register_module()` (validates
  dependencies are already registered), dependency-ordered
  `initialize()`/`start()` (topological sort, cycle-checked),
  `run_health_checks()`, best-effort `shutdown()` (reverse order,
  continues past individual failures, aggregates into one
  `ShutdownError`).

### Bug found and fixed during this milestone

Several logging calls used `extra={"module": ...}`, which collides with
Python's stdlib `logging.LogRecord.module` reserved attribute. This was
latent — masked because `configure_logging()`'s default level filters out
DEBUG/INFO calls before `makeRecord()` is reached — but would have
crashed any ERROR-level log call in production (confirmed via a failing
shutdown-path test). Renamed to `module_name` throughout `kernel/`;
verified via full-codebase grep that no other reserved `LogRecord`
attribute names are used as `extra` keys anywhere.

## Testing

99 kernel tests; 298 tests total across the repository. 97.2% coverage on
`quant_os.kernel` (target: ≥95%); 97% overall repository coverage.
Remaining gaps are defensive branches unreachable through the public API
(enforced by `Container._register`'s exactly-one-of-three invariant) and
unreachable `Protocol` stub bodies.

## Explicitly Out of Scope

Market data, news ingestion, trading, strategies, risk calculations,
broker APIs, portfolio, execution, AI, machine learning, databases, HTTP
APIs, WebSockets, GUI, or any other domain-specific logic. Plugin
*loading* was explicitly deferred — only the interfaces were built.
