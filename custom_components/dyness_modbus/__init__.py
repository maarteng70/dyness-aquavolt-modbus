"""
Main integration setup for Dyness Aquavolt Modbus component.

Handles setting up and unloading config entries, initializing
the data coordinator, and forwarding setup to sensor and other platforms.
"""

import logging

from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusTcpParams

from .const import DEFAULT_UNIT_ID, DOMAIN
from .coordinator import DynessCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "sensor",
    "switch",
    "select",
    "button",
    "number",
    "binary_sensor",
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """General setup of the integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    try:
        unit = async_get_unit(
            hass,
            entry,
            ModbusTcpParams(host=entry.data["host"], port=entry.data["port"]),
            entry.data.get("unit_id", DEFAULT_UNIT_ID),
        )
        coordinator = DynessCoordinator(hass, entry, unit)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

        await coordinator.async_load_registers(None)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        await coordinator.async_config_entry_first_refresh()

        return True
    except Exception as err:
        _LOGGER.error("Error setting up entry %s: %s", entry.entry_id, err)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and its associated platforms."""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id, None)

        return unload_ok
    except Exception as err:
        _LOGGER.error("Error unloading entry %s: %s", entry.entry_id, err)
        return False
