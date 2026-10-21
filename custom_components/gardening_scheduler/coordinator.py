"""Data coordinator and persistent task state."""
from __future__ import annotations

from datetime import date, datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CATEGORIES, CONF_CLIMATE, CONF_HEMISPHERE, CONF_WEATHER_ENTITY,
    DEFAULT_CATEGORIES, DOMAIN, STORAGE_KEY, STORAGE_VERSION,
)
from .tasks import TASKS

_LOGGER = logging.getLogger(__name__)


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
        except (Exception) as err:
            _LOGGER.debug("Daily forecast unavailable: %s", err)

        lows = []
        for item in forecast[:5]:
            value = item.get("templow")
            if value is None:
                value = item.get("temperature")
            try:
                if value is not None:
                    lows.append(float(value))
            except (TypeError, ValueError):
                continue

        current_temp = state.attributes.get("temperature")
        try:
            current_temp = float(current_temp) if current_temp is not None else None
        except (TypeError, ValueError):
            current_temp = None
        frost_risk = (current_temp is not None and current_temp <= 2) or any(low <= 2 for low in lows)

        now = datetime.now().astimezone()
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
            if record.get("completed_on") == date.today().isoformat():
                continue
            if record.get("snoozed_until", "") >= date.today().isoformat():
                continue
            active.append({**task, "completed": False})

        return {
            "tasks": active,
            "task_count": len(active),
            "next_task": active[0]["title"] if active else "No tasks due",
            "weather_entity": weather_entity,
            "weather_state": state.state,
            "temperature": current_temp,
            "forecast_lows": lows,
            "frost_risk": frost_risk,
            "frost_advice": "Potential frost: protect vulnerable plants and check local conditions." if frost_risk else "No frost signal detected in available weather data.",
            "location": settings.get("location", ""),
            "country": settings.get("country", ""),
            "climate": climate,
            "updated": now.isoformat(),
        }

    def complete_task(self, task_id: str) -> None:
        """Mark a task complete for today and persist."""
        self.task_state[task_id] = {"completed_on": date.today().isoformat()}
        self.hass.async_create_task(self.store.async_save(self.task_state))
        self.hass.async_create_task(self.async_request_refresh())

    def snooze_task(self, task_id: str, days: int = 3) -> None:
        """Snooze a task for a bounded number of days."""
        days = max(1, min(int(days), 30))
        self.task_state[task_id] = {"snoozed_until": (date.today() + timedelta(days=days)).isoformat()}
        self.hass.async_create_task(self.store.async_save(self.task_state))
        self.hass.async_create_task(self.async_request_refresh())
