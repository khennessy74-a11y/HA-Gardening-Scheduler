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

# Broad starting defaults only; large or geographically diverse countries stay
# unknown so users can select a more representative local climate profile.
OCEANIC_COUNTRIES = {"GB", "IE", "NZ", "NL", "BE", "DK"}
MEDITERRANEAN_COUNTRIES = {"ES", "PT", "IT", "GR", "CY", "MT"}
CONTINENTAL_COUNTRIES = {"DE", "PL", "CZ", "SK", "HU", "RO", "UA"}
COLD_COUNTRIES = {"IS", "NO", "SE", "FI"}
ARID_COUNTRIES = {"AE", "SA", "QA", "KW", "OM", "BH"}
TROPICAL_COUNTRIES = {"SG", "MY", "TH", "PH", "ID", "LK"}
SUBTROPICAL_COUNTRIES = {"JP", "KR", "TW", "BD"}
SOUTHERN_COUNTRIES = {"AU", "NZ", "ZA", "AR", "CL", "UY", "PY", "BO", "PE"}


def _default_climate(country: str) -> str:
    """Return a broad climate default for onboarding, not a precise local forecast."""
    for countries, climate in (
        (OCEANIC_COUNTRIES, "oceanic"),
        (MEDITERRANEAN_COUNTRIES, "mediterranean"),
        (CONTINENTAL_COUNTRIES, "continental"),
        (COLD_COUNTRIES, "cold"),
        (ARID_COUNTRIES, "arid"),
        (TROPICAL_COUNTRIES, "tropical"),
        (SUBTROPICAL_COUNTRIES, "subtropical"),
    ):
        if country in countries:
            return climate
    return "unknown"


class GardeningConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial setup."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Ask for country and locality first."""
        if user_input is not None:
            country = user_input[CONF_COUNTRY].strip().upper()
            location = user_input[CONF_LOCATION].strip()
            postcode = user_input.get(CONF_POSTCODE, "").strip()
            if not country or not location:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._location_schema(),
                    errors={"base": "location_required"},
                )
            self._location_input = {
                CONF_COUNTRY: country,
                CONF_LOCATION: location,
                CONF_POSTCODE: postcode,
            }
            return await self.async_step_preferences()

        return self.async_show_form(step_id="user", data_schema=self._location_schema())

    def _location_schema(self):
        country_default = getattr(self.hass.config, "country", None) or "GB"
        return vol.Schema({
            vol.Required(CONF_COUNTRY, default=country_default): str,
            vol.Required(CONF_LOCATION): str,
            vol.Optional(CONF_POSTCODE, default=""): str,
        })

    async def async_step_preferences(self, user_input=None):
        """Use the chosen country to preselect broad regional gardening settings."""
        location = getattr(self, "_location_input", {})
        country = location.get(CONF_COUNTRY, "GB")
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Gardening Scheduler — {location[CONF_LOCATION]}",
                data={**location, **user_input},
            )

        hemisphere_default = "southern" if country in SOUTHERN_COUNTRIES else "northern"
        climate_default = _default_climate(country)
        return self.async_show_form(
            step_id="preferences",
            data_schema=vol.Schema({
                vol.Required(CONF_HEMISPHERE, default=hemisphere_default): vol.In(HEMISPHERES),
                vol.Required(CONF_CLIMATE, default=climate_default): vol.In(CLIMATES),
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
            }),
        )

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
