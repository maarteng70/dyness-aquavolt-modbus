"""
Module for creating number entities for Dyness Aquavolt Modbus integration.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberEntity
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
    entities = [DynessNumber(coordinator, definition) for definition in coordinator.NUMBER_DEFINITIONS]
    async_add_entities(entities)


class DynessNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Modbus number entity for Dyness Aquavolt."""

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
        self._attr_native_min_value = self.definition.get('min', 0)
        self._attr_native_max_value = self.definition.get('max', 100)
        self._attr_native_step = self.definition.get('step', 1)
        self._scale = definition.get("scale", 1)
        self._unit = definition.get("unit", None)
        if "category" in self.definition:
            self._attr_entity_category = EntityCategory(self.definition.get("category"))
        if "icon" in self.definition:
            self._attr_icon = self.definition.get("icon")
        if definition.get("enabled_by_default") is False:
            self._attr_entity_registry_enabled_default = False

    @property
    def entity_type(self) -> str:
        return "number"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if data is None:
            return None
        raw_value = data.get(self._key)
        return raw_value * self._scale if raw_value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        raw_value = int(value / self._scale)
        if not isinstance(self.coordinator.data, dict):
            self.coordinator.data = {}
        self.coordinator.data[self._key] = raw_value
        self.async_write_ha_state()
        success = await self.coordinator.async_write_value(
            register=self._register,
            value=raw_value,
            key=self._key,
            scale=self._scale,
            unit=self._unit,
            entity_type=self.entity_type,
        )
        if not success:
            _LOGGER.debug("Write failed for %s, refreshing", self._key)
            await self.coordinator.async_read_value(self.definition, self._key, track_failure=False)

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }
