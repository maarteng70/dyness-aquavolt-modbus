"""
Module for creating switch entities for Dyness Aquavolt battery devices.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.switch import SwitchEntity
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
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [DynessSwitch(coordinator, definition) for definition in coordinator.SWITCH_DEFINITIONS]
    async_add_entities(entities)


class DynessSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Modbus switch entity for Dyness Aquavolt."""

    def __init__(self, coordinator: DynessCoordinator, definition: dict):
        super().__init__(coordinator)
        self._key = definition["key"]
        self.definition = definition
        self.coordinator._entity_types[self._key] = self.entity_type
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self.definition['key']}"
        self._attr_has_entity_name = True
        self._attr_translation_key = definition["key"]
        self._state = None
        self._register = definition["register"]
        if "category" in self.definition:
            self._attr_entity_category = EntityCategory(self.definition.get("category"))
        if "icon" in self.definition:
            self._attr_icon = self.definition.get("icon")
        if definition.get("enabled_by_default") is False:
            self._attr_entity_registry_enabled_default = False

    @property
    def entity_type(self) -> str:
        return "switch"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if data is None or self._key not in data:
            return None
        current_value = data[self._key]
        return current_value == self.definition.get("command_on")

    async def async_turn_on(self, **kwargs) -> None:
        value = self.definition.get("command_on")
        if value is None:
            _LOGGER.error("No command_on value defined for switch %s", self._key)
            return
        self.coordinator.data[self._key] = value
        self.async_write_ha_state()
        await self.coordinator.async_write_value(
            register=self._register,
            value=value,
            key=self._key,
            scale=self.definition.get("scale", 1),
            unit=self.definition.get("unit"),
            entity_type=self.entity_type,
        )

    async def async_turn_off(self, **kwargs) -> None:
        value = self.definition.get("command_off")
        if value is None:
            _LOGGER.error("No command_off value defined for switch %s", self._key)
            return
        self.coordinator.data[self._key] = value
        self.async_write_ha_state()
        await self.coordinator.async_write_value(
            register=self._register,
            value=value,
            key=self._key,
            scale=self.definition.get("scale", 1),
            unit=self.definition.get("unit"),
            entity_type=self.entity_type,
        )

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }
