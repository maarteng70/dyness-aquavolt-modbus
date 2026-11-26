"""
Dyness Aquavolt Modbus sensor entities.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity, EntityCategory
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
    """Set up all Dyness sensors from definitions."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    sensor_groups = (
        (DynessSensor, coordinator.SENSOR_DEFINITIONS),
        (DynessEfficiencySensor, coordinator.EFFICIENCY_SENSOR_DEFINITIONS),
        (DynessSolarPowerSensor, coordinator.SOLAR_POWER_SENSOR_DEFINITIONS),
        (DynessVersionSensor, coordinator.VERSION_SENSOR_DEFINITIONS),
        (DynessStoredEnergySensor, coordinator.STORED_ENERGY_SENSOR_DEFINITIONS),
        (DynessBatteryCycleSensor, coordinator.CYCLE_SENSOR_DEFINITIONS),
    )
    for entity_cls, definitions in sensor_groups:
        entities.extend(entity_cls(coordinator, definition) for definition in definitions)

    async_add_entities(entities)


class DynessSensor(CoordinatorEntity, SensorEntity):
    """Generic Modbus sensor reading from the coordinator."""

    def __init__(self, coordinator: DynessCoordinator, definition: dict):
        super().__init__(coordinator)
        self._key = definition["key"]
        self.definition = definition
        self.coordinator._entity_types[self._key] = self.entity_type
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self.definition['key']}"
        self._attr_has_entity_name = True
        self._attr_translation_key = definition["key"]
        self._attr_native_unit_of_measurement = definition.get("unit")
        self._attr_device_class = definition.get("device_class")
        self._attr_state_class = definition.get("state_class")
        if "category" in definition:
            self._attr_entity_category = EntityCategory(definition["category"])
        if "icon" in definition:
            self._attr_icon = definition["icon"]
        if definition.get("enabled_by_default") is False:
            self._attr_entity_registry_enabled_default = False
        self.states = definition.get("states")

    @property
    def entity_type(self) -> str:
        return "sensor"

    @property
    def available(self) -> bool:
        data = getattr(self.coordinator, "data", None)
        return isinstance(data, dict) and self._key in data

    @property
    def native_value(self):
        if self._key not in self.coordinator.data:
            return None
        value = self.coordinator.data[self._key]

        if self.definition.get("data_type") == "schedule":
            data = getattr(self.coordinator, "data", {}) or {}
            attrs = data.get(f"{self._key}_attrs") or {}
            enabled = None
            if isinstance(attrs, dict) and "enabled" in attrs:
                try:
                    enabled = bool(int(attrs.get("enabled") or 0))
                except Exception:
                    enabled = bool(attrs.get("enabled"))
            else:
                raw = data.get(self._key)
                if isinstance(raw, (list, tuple)) and len(raw) >= 5:
                    try:
                        enabled = bool(int(raw[4]))
                    except Exception:
                        enabled = bool(raw[4])
            if enabled is None:
                return None
            return enabled

        if isinstance(value, (int, float)):
            if self._key == "ems_version":
                try:
                    iv = int(value)
                except Exception:
                    iv = None
                if iv is not None:
                    if iv >= 1000:
                        value = round(iv / 10.0, 1)
                    else:
                        value = int(iv)
                    if isinstance(value, float) and value.is_integer():
                        value = int(value)
                else:
                    pass
            else:
                scale = self.definition.get("scale", 1)
                offset = self.definition.get("offset", 0)
                precision = int(self.definition.get("precision", 0) or 0)
                value = float(value) * scale + offset
                value = round(value, precision)
                if isinstance(value, float) and value.is_integer():
                    value = int(value)

        if self.states and value in self.states:
            return self.states[value]

        return value

    @property
    def suggested_display_precision(self) -> int | None:
        if self.states:
            return None
        return self.definition.get("precision")

    @property
    def suggested_display_unit(self) -> str | None:
        if self.states:
            return None
        return self.definition.get("unit")

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        attrs = data.get(f"{self._key}_attrs") or {}
        if self.definition.get("data_type") == "schedule":
            if not isinstance(attrs, dict) or not attrs:
                raw = data.get(self._key)
                if isinstance(raw, (list, tuple)) and len(raw) >= 5:
                    try:
                        attrs = {
                            "days": int(raw[0]),
                            "start": int(raw[1]),
                            "end": int(raw[2]),
                            "mode": int(raw[3]) - 0x10000 if int(raw[3]) >= 0x8000 else int(raw[3]),
                            "enabled": int(raw[4]),
                        }
                    except Exception:
                        attrs = {}
            if isinstance(attrs, dict) and attrs:
                def _fmt_time(t):
                    try:
                        t = int(t)
                        if 0 <= t <= 2359 and (t % 100) < 60:
                            hh = t // 100
                            mm = t % 100
                        else:
                            hh = t // 60
                            mm = t % 60
                        return f"{hh:02d}:{mm:02d}"
                    except Exception:
                        return t
                days = attrs.get("days")
                try:
                    dmask = int(days) if days is not None else 0
                except Exception:
                    dmask = 0
                weekday_names_mon = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                selected_mon = [weekday_names_mon[i] for i in range(7) if (dmask >> i) & 1]
                display_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                selected = [d for d in display_order if d in selected_mon]
                enriched = {}
                enriched["days_list"] = selected
                enriched["start_time"] = _fmt_time(attrs.get("start"))
                enriched["end_time"] = _fmt_time(attrs.get("end"))
                mode_raw = attrs.get("mode")
                mode = None
                power = None
                try:
                    if mode_raw is not None:
                        m = int(mode_raw)
                        if m == -1:
                            mode = "self consumption"
                        elif m < 0:
                            mode = "charge"
                            power = abs(m)
                        else:
                            mode = "discharge"
                            power = m
                except Exception:
                    mode = None
                    power = None
                enriched["mode"] = mode
                enriched["power"] = power
                enriched["enabled"] = bool(attrs.get("enabled"))
                return enriched
        return attrs or {}


class DynessCalculatedSensor(CoordinatorEntity, SensorEntity):
    """Base class for calculated sensors."""

    def __init__(self, coordinator: DynessCoordinator, definition: dict):
        super().__init__(coordinator)
        self._key = definition["key"]
        self.definition = definition
        self.coordinator._entity_types[self._key] = self.entity_type
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self.definition['key']}"
        self._attr_has_entity_name = True
        self._attr_translation_key = definition["key"]
        self._attr_native_unit_of_measurement = definition.get("unit")
        self._attr_device_class = definition.get("device_class")
        self._attr_state_class = definition.get("state_class")
        if "category" in definition:
            self._attr_entity_category = EntityCategory(definition["category"])
        if "icon" in definition:
            self._attr_icon = definition["icon"]
        if definition.get("enabled_by_default") is False:
            self._attr_entity_registry_enabled_default = False
        for alias, dep_key in self.get_dependency_keys().items():
            if not dep_key:
                continue
            self.coordinator._entity_types[dep_key] = "sensor"
            if not hasattr(self, "_all_definitions"):
                self._all_definitions = (
                    self.coordinator.SENSOR_DEFINITIONS + self.coordinator.BINARY_SENSOR_DEFINITIONS
                )
            all_definitions = self._all_definitions
            scale = next((d.get("scale", 1) for d in all_definitions if d.get("key") == dep_key), None)
            scale = scale or self.definition.get("dependency_defs", {}).get(alias, 1)
            self.coordinator._scales[dep_key] = scale

    def get_dependency_keys(self):
        return self.definition.get("dependency_keys", {})

    @property
    def entity_type(self) -> str:
        return "sensor"

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": self.coordinator.config_entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "entry_type": "service",
        }

    def _handle_coordinator_update(self) -> None:
        if not getattr(self.coordinator, "last_update_success", False):
            self._attr_native_value = None
            self.async_write_ha_state()
            return
        data = self.coordinator.data if isinstance(self.coordinator.data, dict) else {}
        self._calculate(data)
        self.async_write_ha_state()

    def _calculate(self, data: dict) -> None:
        dependency_keys = self.get_dependency_keys()
        dep_values = {}
        missing = []
        for alias, actual_key in dependency_keys.items():
            val = data.get(actual_key)
            scale = self.coordinator._scales.get(actual_key, 1)
            if val is None:
                missing.append(alias)
            else:
                dep_values[alias] = float(val) * scale
        if missing:
            _LOGGER.warning("%s missing required value(s): %s", self._key, ", ".join(missing))
            self._attr_native_value = None
            return
        try:
            value = self.calculate_value(dep_values)
            _LOGGER.debug("Calculated value for %s: %s", self._key, value)
            self._attr_native_value = value
        except Exception as ex:
            _LOGGER.warning("Error calculating sensor %s: %s", self._key, ex)
            self._attr_native_value = None

    def calculate_value(self, dep_values: dict):
        raise NotImplementedError


class DynessSolarPowerSensor(DynessCalculatedSensor):
    def calculate_value(self, dep_values: dict):
        aliases = list(self.get_dependency_keys().keys())
        values = [dep_values.get(alias) for alias in aliases]
        if any(value is None for value in values):
            return None
        total = round(sum(float(value) for value in values), 2)
        self._attr_native_value = total
        return total


class DynessStoredEnergySensor(DynessCalculatedSensor):
    def calculate_value(self, dep_values: dict):
        soc = dep_values.get("soc")
        capacity = dep_values.get("capacity")
        stored_energy = round((soc / 100) * capacity, 2)
        self._attr_native_value = stored_energy
        return stored_energy


class DynessEfficiencySensor(DynessCalculatedSensor):
    def calculate_value(self, dep_values: dict):
        mode = self.definition.get("mode", "round_trip")
        if mode == "round_trip":
            charge = dep_values.get("charge")
            discharge = dep_values.get("discharge")
            if charge in (None, 0):
                return None
            efficiency = (discharge / charge) * 100
        elif mode == "conversion":
            battery_power = dep_values.get("battery_power")
            ac_power = dep_values.get("ac_power")
            if battery_power is None or ac_power is None:
                return None
            if battery_power > 0:
                if ac_power == 0:
                    return None
                efficiency = abs(battery_power) / abs(ac_power) * 100
            else:
                if battery_power == 0:
                    return None
                efficiency = abs(ac_power) / abs(battery_power) * 100
        else:
            _LOGGER.warning("%s unknown efficiency mode '%s'", self._key, mode)
            return None
        efficiency_rounded = round(min(efficiency, 100.0), 1)
        self._attr_native_value = efficiency_rounded
        return efficiency_rounded


class DynessBatteryCycleSensor(DynessCalculatedSensor):
    def calculate_value(self, dep_values: dict):
        discharge = dep_values.get("discharge")
        capacity = dep_values.get("capacity")
        if discharge is None or capacity in (None, 0):
            return None
        cycles = round(discharge / capacity, 2)
        self._attr_native_value = cycles
        return cycles


class DynessVersionSensor(DynessCalculatedSensor):
    def _calculate(self, data: dict) -> None:
        dependency_keys = self.get_dependency_keys()
        raw_values = {}
        for alias, actual_key in dependency_keys.items():
            val = data.get(actual_key)
            if val is None:
                return
            raw_values[alias] = val
        try:
            self._attr_native_value = self.calculate_value(raw_values)
        except Exception as ex:
            _LOGGER.warning("Error building version string for %s: %s", self._key, ex)
            self._attr_native_value = None

    def calculate_value(self, raw_values: dict):
        mode = self.definition.get("mode")
        if mode == "dsp_arm_bms_modbus":
            dsp1_raw = int(raw_values.get("dsp1", 0))
            dsp2_raw = int(raw_values.get("dsp2", 0))
            arm_raw = int(raw_values.get("arm", 0))
            bms_raw = int(raw_values.get("bms", 0))
            modbus_raw = int(raw_values.get("modbus", 0))
            return f"{dsp1_raw}.{dsp2_raw}.{arm_raw}-{bms_raw}.{modbus_raw}"
        elif mode in ("dsp_arm_bms", "ems_vms_bms"):
            dsp1_raw = int(raw_values.get("dsp1", 0))
            dsp2_raw = int(raw_values.get("dsp2", 0))
            arm_raw = int(raw_values.get("arm", 0))
            bms_raw = int(raw_values.get("bms", 0))
            return f"V{dsp1_raw}.{dsp2_raw}.{arm_raw}.{bms_raw}"
        _LOGGER.warning("%s unknown version mode '%s'", self._key, mode)
        return None
