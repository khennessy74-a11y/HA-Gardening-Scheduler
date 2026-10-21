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
        """Collect the user's location and local weather source."""
        if user_input is not None:
            country = user_input[CONF_COUNTRY].strip().upper()
            location = user_input[CONF_LOCATION].strip()
            postcode = user_input.get(CONF_POSTCODE, "").strip()
            if not country or not location:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._schema(),
                    errors={"base": "location_required"},
                )
            user_input[CONF_COUNTRY] = country
            user_input[CONF_LOCATION] = location
            user_input[CONF_POSTCODE] = postcode
            # A single config entry avoids duplicate service registration. The
            # location and climate profile can be changed later in Options.
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Gardening Scheduler — {location}",
                data=user_input,
            )

        return self.async_show_form(step_id="user", data_schema=self._schema())

    def _schema(self):
        """Build form with defaults derived from Home Assistant's configured location."""
        latitude = getattr(self.hass.config, "latitude", 0.0)
        country_default = getattr(self.hass.config, "country", None) or "GB"
        hemisphere_default = "southern" if latitude < 0 else "northern"
        return vol.Schema({
            vol.Required(CONF_COUNTRY, default=country_default): str,
            vol.Required(CONF_LOCATION): str,
            vol.Optional(CONF_POSTCODE, default=""): str,
            vol.Required(CONF_HEMISPHERE, default=hemisphere_default): vol.In(HEMISPHERES),
            vol.Required(CONF_CLIMATE, default="unknown"): vol.In(CLIMATES),
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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow."""
        return GardeningOptionsFlow()


class GardeningOptionsFlow(config_entries.OptionsFlow):
    """Allow the location, weather source and categories to be changed later."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            user_input[CONF_COUNTRY] = user_input[CONF_COUNTRY].strip().upper()
            user_input[CONF_LOCATION] = user_input[CONF_LOCATION].strip()
            user_input[CONF_POSTCODE] = user_input.get(CONF_POSTCODE, "").strip()
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
