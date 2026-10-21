"""Data coordinator and persistent task state."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CATEGORIES, CONF_CLIMATE, CONF_HEMISPHERE, CONF_WEATHER_ENTITY,
    DEFAULT_CATEGORIES, DOMAIN, STORAGE_KEY, STORAGE_VERSION,
)
from .tasks import TASKS

_LOGGER = logging.getLogger(__name__)
FROST_THRESHOLD_C = 2.0


class GardeningCoordinator(DataUpdateCoordinator):
    """Fetch weather and derive gardening advice."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry.entry_id}")
        self.task_state: dict = {}
        self._store_loaded = False
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=6))

    @property
    def settings(self) -> dict:
        return {**self.entry.data, **self.entry.options}

    def _celsius(self, value):
        """Convert Home Assistant's configured temperature unit to Celsius."""
        if value is None:
            return None
        try:
            temperature = float(value)
        except (TypeError, ValueError):
            return None
        unit = str(self.hass.config.units.temperature_unit).strip().lower()
        if unit in {"°f", "f", "fahrenheit"}:
            return (temperature - 32.0) * 5.0 / 9.0
        return temperature

    async def _async_update_data(self) -> dict:
        if not self._store_loaded:
            self.task_state = await self.store.async_load() or {}
            self._store_loaded = True

        settings = self.settings
        weather_entity = settings.get(CONF_WEATHER_ENTITY)
        state = self.hass.states.get(weather_entity) if weather_entity else None
        if state is None:
            raise UpdateFailed(f"Weather entity unavailable: {weather_entity}")

        forecast = []
        try:
            response = await self.hass.services.async_call(
                "weather", "get_forecasts",
                {"entity_id": weather_entity, "type": "daily"},
                blocking=True, return_response=True,
            )
            if isinstance(response, dict):
                entity_forecast = response.get(weather_entity, {})
                forecast = entity_forecast.get("forecast", []) or []
        except Exception as err:
            _LOGGER.debug("Daily forecast unavailable: %s", err)

        # A daily high is not a safe substitute for a missing overnight low.
        lows = []
        for item in forecast[:5]:
            low = self._celsius(item.get("templow"))
            if low is not None:
                lows.append(low)

        current_temp = self._celsius(state.attributes.get("temperature"))
        if current_temp is not None and current_temp <= FROST_THRESHOLD_C:
            frost_status = "risk"
        elif lows:
            frost_status = "risk" if any(low <= FROST_THRESHOLD_C for low in lows) else "none_detected"
        else:
            frost_status = "unknown"

        now = dt_util.now()
        today = now.date().isoformat()
        month = now.month
        if settings.get(CONF_HEMISPHERE, "northern") == "southern":
            month = ((month + 5) % 12) + 1

        categories = set(settings.get(CONF_CATEGORIES, DEFAULT_CATEGORIES))
        climate = settings.get(CONF_CLIMATE, "unknown")
        active = []
        for task in TASKS:
            if task["category"] not in categories or month not in task["months"]:
                continue
            if "all" not in task["climates"] and climate not in task["climates"] and climate != "unknown":
                continue
            record = self.task_state.get(task["id"], {})
            if record.get("completed_on") == today:
                continue
            if record.get("snoozed_until", "") >= today:
                continue
            active.append({**task, "completed": False})

        advice = {
            "risk": "Potential frost: protect vulnerable plants and check local conditions.",
            "none_detected": "No frost signal in the available overnight forecast. Check local conditions for exposed areas.",
            "unknown": "Overnight forecast lows are unavailable; check your local forecast before leaving tender plants outside.",
        }[frost_status]

        return {
            "tasks": active,
            "task_count": len(active),
            "next_task": active[0]["title"] if active else "No tasks due",
            "weather_entity": weather_entity,
            "weather_state": state.state,
            "temperature_c": current_temp,
            "forecast_lows_c": lows,
            "frost_status": frost_status,
            "frost_advice": advice,
            "location": settings.get("location", ""),
            "country": settings.get("country", ""),
            "climate": climate,
            "updated": now.isoformat(),
        }

    def complete_task(self, task_id: str) -> None:
        """Mark a task complete for today and persist."""
        self.task_state[task_id] = {"completed_on": dt_util.now().date().isoformat()}
        self.hass.async_create_task(self.store.async_save(self.task_state))
        self.hass.async_create_task(self.async_request_refresh())

    def snooze_task(self, task_id: str, days: int = 3) -> None:
        """Snooze a task for a bounded number of days."""
        days = max(1, min(int(days), 30))
        self.task_state[task_id] = {
            "snoozed_until": (dt_util.now().date() + timedelta(days=days)).isoformat()
        }
        self.hass.async_create_task(self.store.async_save(self.task_state))
        self.hass.async_create_task(self.async_request_refresh())
