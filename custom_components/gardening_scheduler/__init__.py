"""Gardening Scheduler integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN, PLATFORMS
from .coordinator import GardeningCoordinator

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=6)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration-level services."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gardening Scheduler from a config entry."""
    coordinator = GardeningCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def complete_task(call: ServiceCall) -> None:
        task_id = call.data.get("task_id")
        if not task_id:
            return
        coordinator.complete_task(task_id)

    async def snooze_task(call: ServiceCall) -> None:
        task_id = call.data.get("task_id")
        days = call.data.get("days", 3)
        if task_id:
            coordinator.snooze_task(task_id, days)

    async def refresh(call: ServiceCall) -> None:
        await coordinator.async_request_refresh()

    for service, handler in (
        ("complete_task", complete_task),
        ("snooze_task", snooze_task),
        ("refresh", refresh),
    ):
        hass.services.async_register(DOMAIN, service, handler)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
