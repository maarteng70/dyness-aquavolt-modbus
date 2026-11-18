"""
Module for creating button entities for Dyness Aquavolt Modbus integration.
"""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DynessCoordinator
from .const import DOMAIN, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [DynessButton(coordinator, definition) for definition in coordinator.BUTTON_DEFINITIONS]
    async_add_entities(entities)


class DynessButton(ButtonEntity):
    """ButtonEntity to trigger actions on the Dyness Aquavolt."""

    def __init__(self, coordinator: DynessCoordinator, definition: dict):
        self.coordinator = coordinator
        self._key = definition["key"]
        self.definition = definition
        self._command = definition.get("command", 1)
        self._register = definition["register"]
        self.coordinator._entity_types[self._key] = "button"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self._key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = definition["key"]
        if "category" in self.definition:
            self._attr_entity_category = EntityCategory(self.definition.get("category"))
        if "icon" in self.definition:
            self._attr_icon = self.definition.get("icon")
        if definition.get("enabled_by_default") is False:
            self._attr_entity_registry_enabled_default = False

    @property
    def entity_type(self) -> str:
        return "button"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        success = await self.coordinator.async_write_value(
            register=self._register,
            value=self._command,
            key=self._key,
            scale=self.definition.get("scale", 1),
            unit=self.definition.get("unit"),
            entity_type=self.entity_type,
        )
        if success:
            import asyncio
            _LOGGER.debug("Successfully wrote value %s to register %s", self._command, self._register)
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to write value %s to register %s", self._command, self._register)

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }
