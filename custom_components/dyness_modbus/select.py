"""
Module for creating select entities for Dyness Aquavolt Modbus integration.
"""

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import DynessCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DynessCoordinator = hass.data[DOMAIN][entry.entry_id]

    sel_defs = getattr(coordinator, "SELECT_DEFINITIONS", None)
    try:
        if isinstance(sel_defs, dict):
            normalized: list[dict[str, Any]] = []
            for key, definition in sel_defs.items():
                d = dict(definition or {})
                d.setdefault("key", key)
                normalized.append(d)
            sel_defs = normalized
        elif isinstance(sel_defs, list):
            for d in sel_defs:
                if "key" not in d:
                    raise ValueError(f"Select definition without 'key': {d}")
        else:
            _LOGGER.error("SELECT_DEFINITIONS is empty or unknown type: %r", type(sel_defs))
            sel_defs = []
    except Exception as err:
        _LOGGER.exception("Error normalising SELECT_DEFINITIONS: %s", err)
        sel_defs = []

    entities: list[DynessSelect] = []
    for definition in sel_defs:
        try:
            entities.append(DynessSelect(coordinator, definition))
        except Exception as err:
            _LOGGER.exception("Error creating select entity from %r: %s", definition, err)

    if entities:
        async_add_entities(entities, update_before_add=True)


class DynessSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Modbus select entity for Dyness Aquavolt."""

    def __init__(self, coordinator: DynessCoordinator, definition: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._key = definition["key"]
        self.definition = definition
        if not hasattr(self.coordinator, "_entity_types") or self.coordinator._entity_types is None:
            self.coordinator._entity_types = {}
        self.coordinator._entity_types[self._key] = self.entity_type
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self._key}"
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
        self._attr_suggested_object_id = definition["key"]
        self._attr_options = list(self.definition.get("options", {}).keys())

    @property
    def entity_type(self) -> str:
        return "select"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def options(self) -> list[str]:
        return list(self.definition.get("options", {}).keys())

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if data is None:
            return None
        value = data.get(self._key)
        if value is None:
            return None
        options_map = self.definition.get("options", {})
        try:
            reversed_map = {int(v): k for k, v in options_map.items()}
            return reversed_map.get(int(value))
        except Exception:
            _LOGGER.debug("current_option: value=%r does not match options_map=%r", value, options_map)
            return None

    async def async_select_option(self, option: str) -> None:
        options_map = self.definition.get("options", {})
        if option not in options_map:
            _LOGGER.warning("Invalid option '%s' for %s", option, self._key)
            return
        value = options_map[option]
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
            "entry_type": DeviceEntryType.SERVICE,
        }
