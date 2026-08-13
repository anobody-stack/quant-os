# QuantOS — Project Bible

This document defines the mission, principles, and standards that govern all
work on QuantOS. It is the reference point for every contributor and every
architectural or engineering decision. It does not describe implementation
details — those live in `docs/architecture/` and `docs/decisions/`.

## Mission

Build a modular financial operating system capable of institutional-grade
research, analysis, risk management, and automated trading — starting with
Gold and Crude Oil, and extensible to any future asset class.

## Vision

QuantOS becomes the single operating layer a trading desk relies on: one
system for data, research, risk, portfolio, reporting, and execution —
replacing fragmented tools with a coherent, well-tested, auditable codebase
that scales from one asset to a full multi-asset operation.

## Core Principles

- **Correctness before speed.** Financial correctness is never sacrificed for
  performance or convenience.
- **Determinism.** Given the same inputs, the system produces the same
  outputs. No hidden state, no hidden side effects.
- **Explicitness.** Explicit is better than implicit. No magic, no
  convention-over-configuration tricks that obscure behavior.
- **Modularity.** Each module owns a single, well-defined responsibility and
  is independently testable.
- **Extensibility by design.** New asset classes, data sources, brokers, and
  strategies must be addable without restructuring existing modules.
- **Auditability.** Every material decision, calculation, and trade must be
  traceable.

## Coding Standards

- Python 3.12+, fully typed, PEP 8 compliant.
- `Decimal` for all financial values — never floating point.
- UTC timestamps everywhere.
- `pathlib` for filesystem paths.
- Enums instead of magic strings.
- No global mutable state.
- No mutable default arguments.
- Every public class and function is documented.
- No unexplained TODOs left in merged code.

## Architecture Rules

- Architecture is authoritative and is defined centrally, not per-contributor.
- Module boundaries are respected: a module may not silently take on
  responsibilities that belong to another module.
- Dependencies flow in one direction only, as defined by the architecture
  documentation in `docs/architecture/`.
- Any perceived conflict between a task and the architecture must be raised
  and resolved before implementation continues — never silently worked
  around.

## Development Workflow

- All work is scoped to a milestone, defined in `docs/milestones/` before
  implementation begins.
- Significant architectural or design decisions are recorded as Architecture
  Decision Records (ADRs) in `docs/decisions/`.
- Ambiguity in a specification is resolved by asking, not by assuming.
- Changes are scoped tightly: only the files necessary for the task at hand
  are modified.
- Every change is reflected in `CHANGELOG.md`.

## Testing Philosophy

- Every unit of behavior is covered by a test.
- Unit tests (`tests/unit/`) verify isolated logic with no external
  dependencies.
- Integration tests (`tests/integration/`) verify components working
  together, including any external system boundaries.
- Test coverage must never decrease as a result of a change.
- Tests must be deterministic and reproducible — no reliance on real network
  calls, wall-clock time, or external services.

## Future Modules

The following functional areas are established as placeholders and will be
built out in future milestones:

- **core** — domain primitives and shared abstractions.
- **data** — market data acquisition, normalization, and storage.
- **trading** — order management and execution.
- **risk** — risk measurement, limits, and exposure management.
- **reporting** — report generation and formatting.
- **ai** — AI/ML-driven research and decision support.
- **portfolio** — portfolio construction, tracking, and accounting.
- **infrastructure** — integrations with brokers, data vendors, and storage.
- **utils** — cross-cutting, dependency-free utilities.
