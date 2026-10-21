"""Constants for Gardening Scheduler."""
from __future__ import annotations

DOMAIN = "gardening_scheduler"
PLATFORMS = ["sensor"]
CONF_COUNTRY = "country"
CONF_LOCATION = "location"
CONF_POSTCODE = "postcode"
CONF_HEMISPHERE = "hemisphere"
CONF_CLIMATE = "climate"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_NOTIFY_SERVICE = "notify_service"
CONF_CATEGORIES = "categories"

HEMISPHERES = ["northern", "southern"]
CLIMATES = [
    "oceanic",
    "mediterranean",
    "continental",
    "subtropical",
    "tropical",
    "arid",
    "cold",
    "unknown",
]
CATEGORIES = {
    "fruit_trees": "Fruit trees",
    "fruit_bushes": "Fruit bushes",
    "vegetables": "Vegetables",
    "seeds_seedlings": "Seeds and seedlings",
    "flowers_bulbs": "Flowers and bulbs",
    "shrubs_hedges": "Shrubs and hedges",
    "lawn": "Lawn",
    "houseplants": "Houseplants and tender plants",
    "general": "General garden care",
}
DEFAULT_CATEGORIES = list(CATEGORIES)
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.task_state"
