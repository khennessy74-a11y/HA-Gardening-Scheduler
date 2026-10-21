"""Gardening Scheduler integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS
from .coordinator import GardeningCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration-level services."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gardening Scheduler from a config entry."""
    coordinator = GardeningCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    def active_coordinator():
        """Resolve the currently loaded coordinator when a service is called."""
        return next(iter(hass.data.get(DOMAIN, {}).values()), None)

    async def complete_task(call: ServiceCall) -> None:
        current = active_coordinator()
        task_id = call.data.get("task_id")
        if current and task_id:
            current.complete_task(task_id)

    async def snooze_task(call: ServiceCall) -> None:
        current = active_coordinator()
        task_id = call.data.get("task_id")
        days = call.data.get("days", 3)
        if current and task_id:
            current.snooze_task(task_id, days)

    async def refresh(call: ServiceCall) -> None:
        current = active_coordinator()
        if current:
            await current.async_request_refresh()

    for service, handler in (
        ("complete_task", complete_task),
        ("snooze_task", snooze_task),
        ("refresh", refresh),
    ):
        if not hass.services.has_service(DOMAIN, service):
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
