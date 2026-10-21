"""Sensors for Gardening Scheduler."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GardeningCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dashboard sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        GardeningTasksSensor(coordinator, entry),
        GardeningNextTaskSensor(coordinator, entry),
        GardeningFrostSensor(coordinator, entry),
    ])


class GardeningBaseSensor(CoordinatorEntity, SensorEntity):
    """Shared sensor metadata."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, name, icon):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_icon = icon


class GardeningTasksSensor(GardeningBaseSensor):
    """Number of currently suggested gardening tasks."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "tasks_due", "Tasks due", "mdi:flower")

    @property
    def native_value(self):
        return self.coordinator.data.get("task_count", 0) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "tasks": self.coordinator.data.get("tasks", []),
            "location": self.coordinator.data.get("location"),
            "country": self.coordinator.data.get("country"),
            "climate": self.coordinator.data.get("climate"),
        }


class GardeningNextTaskSensor(GardeningBaseSensor):
    """Next suggested gardening task."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "next_task", "Next task", "mdi:calendar-check")

    @property
    def native_value(self):
        return self.coordinator.data.get("next_task", "Unknown") if self.coordinator.data else "Unknown"


class GardeningFrostSensor(GardeningBaseSensor):
    """Frost guidance based on current temperature and available daily lows."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "frost_risk", "Frost risk", "mdi:snowflake-alert")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "unknown"
        return self.coordinator.data.get("frost_status", "unknown")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "advice": self.coordinator.data.get("frost_advice"),
            "forecast_lows_c": self.coordinator.data.get("forecast_lows_c", []),
            "temperature_c": self.coordinator.data.get("temperature_c"),
            "temperature_unit": "°C",
            "weather_entity": self.coordinator.data.get("weather_entity"),
        }
