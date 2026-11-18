"""
Module for creating binary sensor entities for Dyness Aquavolt Modbus integration.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
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
    entities = [DynessBinarySensor(coordinator, definition) for definition in coordinator.BINARY_SENSOR_DEFINITIONS]
    entities.append(DynessConnectionBinarySensor(coordinator))
    async_add_entities(entities)


class DynessBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Modbus binary sensor entity for Dyness Aquavolt."""

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
        return "binary_sensor"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if data is None:
            return None
        return bool(data.get(self._key)) if self._key in data else None

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }


class DynessConnectionBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Diagnostic binary sensor exposing Modbus connection health."""

    def __init__(self, coordinator: DynessCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_modbus_connection"
        self._attr_has_entity_name = True
        self._attr_translation_key = "modbus_connection"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_connection_healthy()

    @property
    def extra_state_attributes(self) -> dict:
        return self.coordinator.get_connection_health_attributes()

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }
