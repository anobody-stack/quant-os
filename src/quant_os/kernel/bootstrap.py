"""Bootstrap: wires core kernel services into a fresh container.

Configuration binding lives here: :func:`build_container` resolves
application :class:`~quant_os.core.config.Settings` once and registers the
concrete instance, so modules receive configuration via constructor
injection rather than calling :func:`~quant_os.core.config.get_settings`
themselves.
"""

from __future__ import annotations

from quant_os.core.config import Settings, get_settings
from quant_os.core.logging import get_logger
from quant_os.events import AsyncEventBus, EventBus
from quant_os.kernel.container import Container
from quant_os.kernel.health import HealthAggregator
from quant_os.kernel.lifecycle import LifecycleManager

_logger = get_logger(__name__)


def build_container(settings: Settings | None = None) -> Container:
    """Build a fresh container with core kernel services registered.

    Registers, all as singletons:

    - :class:`~quant_os.core.config.Settings` (configuration binding)
    - :class:`~quant_os.events.EventBus` (backed by
      :class:`~quant_os.events.AsyncEventBus`)
    - :class:`~quant_os.kernel.lifecycle.LifecycleManager`
    - :class:`~quant_os.kernel.health.HealthAggregator`

    Args:
        settings: The settings instance to bind. Defaults to
            :func:`~quant_os.core.config.get_settings` (the process-wide
            singleton) when not provided.

    Returns:
        A :class:`Container` with core kernel services registered, ready
        for modules to be registered on top of.
    """
    container = Container()
    resolved_settings = settings if settings is not None else get_settings()

    container.register_singleton(Settings, instance=resolved_settings)
    container.register_singleton(EventBus, implementation=AsyncEventBus)
    container.register_singleton(LifecycleManager, implementation=LifecycleManager)
    container.register_singleton(HealthAggregator, implementation=HealthAggregator)

    _logger.info(
        "Kernel container bootstrapped",
        extra={"environment": resolved_settings.environment.value},
    )
    return container
