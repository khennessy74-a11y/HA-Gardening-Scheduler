"""Sensors for Gardening Scheduler."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GardeningCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        GardeningTasksSensor(coordinator, entry),
        GardeningNextTaskSensor(coordinator, entry),
        GardeningFrostSensor(coordinator, entry),
    ])


class GardeningBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, name, icon):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_icon = icon


class GardeningTasksSensor(GardeningBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "tasks_due", "Tasks due", "mdi:flower")
        self._attr_native_unit_of_measurement = "tasks"

    @property
    def native_value(self):
        return self.coordinator.data.get("task_count", 0) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        return {
            "tasks": self.coordinator.data.get("tasks", []),
            "location": self.coordinator.data.get("location"),
            "country": self.coordinator.data.get("country"),
            "climate": self.coordinator.data.get("climate"),
        } if self.coordinator.data else {}


class GardeningNextTaskSensor(GardeningBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "next_task", "Next task", "mdi:calendar-check")

    @property
    def native_value(self):
        return self.coordinator.data.get("next_task", "Unknown") if self.coordinator.data else "Unknown"


class GardeningFrostSensor(GardeningBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "frost_risk", "Frost risk", "mdi:snowflake-alert")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "unknown"
        return "risk" if self.coordinator.data.get("frost_risk") else "none_detected"

    @property
    def extra_state_attributes(self):
        return {
            "advice": self.coordinator.data.get("frost_advice"),
            "forecast_lows": self.coordinator.data.get("forecast_lows", []),
            "weather_entity": self.coordinator.data.get("weather_entity"),
        } if self.coordinator.data else {}
