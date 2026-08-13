"""Core infrastructure shared across all QuantOS modules.

Subpackages:
    config: Typed, environment-driven application configuration.
    exceptions: The QuantOS exception hierarchy.
    identifiers: Generic typed identifier primitives.
    logging: Structured logging configuration and logger factory.
    time: Timezone-aware time utilities.
    types: Generic, reusable value types (Money, Price, Percentage, ...).
    validation: Reusable validation helper functions.

Nothing in this package has any knowledge of trading, assets, or any other
financial domain concept.
"""
