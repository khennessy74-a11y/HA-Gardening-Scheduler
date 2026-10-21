"""Config flow for Gardening Scheduler."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CATEGORIES, CLIMATES, CONF_CATEGORIES, CONF_CLIMATE, CONF_COUNTRY,
    CONF_HEMISPHERE, CONF_LOCATION, CONF_NOTIFY_SERVICE, CONF_POSTCODE,
    CONF_WEATHER_ENTITY, DEFAULT_CATEGORIES, DOMAIN, HEMISPHERES,
)


class GardeningConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial setup."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Collect location and local weather source before enabling tasks."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_COUNTRY].lower()}:{user_input[CONF_LOCATION].strip().lower()}:{user_input.get(CONF_POSTCODE, '').strip().lower()}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Gardening Scheduler — {user_input[CONF_LOCATION]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_COUNTRY, default="GB"): str,
            vol.Required(CONF_LOCATION): str,
            vol.Optional(CONF_POSTCODE, default=""): str,
            vol.Required(CONF_HEMISPHERE, default="northern"): vol.In(HEMISPHERES),
            vol.Required(CONF_CLIMATE, default="oceanic"): vol.In(CLIMATES),
            vol.Required(CONF_WEATHER_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="weather")
            ),
            vol.Optional(CONF_NOTIFY_SERVICE, default=""): str,
            vol.Required(CONF_CATEGORIES, default=DEFAULT_CATEGORIES): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[{"value": key, "label": label} for key, label in CATEGORIES.items()],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GardeningOptionsFlow(config_entry)


class GardeningOptionsFlow(config_entries.OptionsFlow):
    """Allow categories and local setup to be changed later."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema({
            vol.Required(CONF_COUNTRY, default=current.get(CONF_COUNTRY, "GB")): str,
            vol.Required(CONF_LOCATION, default=current.get(CONF_LOCATION, "")): str,
            vol.Optional(CONF_POSTCODE, default=current.get(CONF_POSTCODE, "")): str,
            vol.Required(CONF_HEMISPHERE, default=current.get(CONF_HEMISPHERE, "northern")): vol.In(HEMISPHERES),
            vol.Required(CONF_CLIMATE, default=current.get(CONF_CLIMATE, "unknown")): vol.In(CLIMATES),
            vol.Required(CONF_WEATHER_ENTITY, default=current.get(CONF_WEATHER_ENTITY)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="weather")
            ),
            vol.Optional(CONF_NOTIFY_SERVICE, default=current.get(CONF_NOTIFY_SERVICE, "")): str,
            vol.Required(CONF_CATEGORIES, default=current.get(CONF_CATEGORIES, DEFAULT_CATEGORIES)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[{"value": key, "label": label} for key, label in CATEGORIES.items()],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
