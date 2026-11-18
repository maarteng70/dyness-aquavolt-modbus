"""
Handles all sensor polling via Home Assistant DataUpdateCoordinator,
with per-sensor intervals and optional skipping if not due.
"""

import asyncio
import logging
from datetime import timedelta
from time import perf_counter

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVALS, DEFAULT_UNIT_ID

from .helpers.modbus_client import DynessModbusClient
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


def get_entity_type(entity) -> str:
    """Determine entity type based on its class inheritance."""
    for base in entity.__class__.__mro__:
        if issubclass(base, Entity) and base.__name__.endswith("Entity"):
            return base.__name__.replace("Entity", "").lower()
    return "entity"


class DynessCoordinator(DataUpdateCoordinator):
    """Coordinator managing all Dyness Aquavolt Modbus sensors."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, unit):
        """Initialize the coordinator with connection parameters and update interval."""
        self.hass = hass
        entry_data = entry.data or {}

        self.host = entry_data.get("host")
        self.port = entry_data.get("port")
        if self.host is None or self.port is None:
            raise ValueError(
                "Config entry is missing required connection data (host/port). "
                "Please reconfigure the Dyness integration."
            )

        self.message_wait_ms = entry_data.get("message_wait_milliseconds")
        self.unit_id = entry_data.get("unit_id", DEFAULT_UNIT_ID)
        self.unit = unit

        self._entity_types: dict[str, str] = {}
        self.config_entry = entry
        self._scales: dict[str, float] = {}

        # Load register definitions (single model, no version selection)
        self.SENSOR_DEFINITIONS = []
        self.BINARY_SENSOR_DEFINITIONS = []
        self.SELECT_DEFINITIONS = []
        self.SWITCH_DEFINITIONS = []
        self.NUMBER_DEFINITIONS = []
        self.BUTTON_DEFINITIONS = []
        self.EFFICIENCY_SENSOR_DEFINITIONS = []
        self.SOLAR_POWER_SENSOR_DEFINITIONS = []
        self.VERSION_SENSOR_DEFINITIONS = []
        self.STORED_ENERGY_SENSOR_DEFINITIONS = []
        self.CYCLE_SENSOR_DEFINITIONS = []

        self._all_definitions = []

        self.client = DynessModbusClient(
            self.unit,
            self.host,
            self.port,
            message_wait_ms=self.message_wait_ms,
            unit_id=self.unit_id,
        )

        self.data: dict = {}
        self._last_update_times: dict = {}
        self._last_write_times: dict = {}
        self._read_start_times: dict = {}
        self._post_write_refresh_task = None

        self._consecutive_failures = 0
        self._max_consecutive_failures = 5
        self._connection_suspended = False
        self._suspension_reset_time = None
        self._consecutive_timeout_cycles = 0
        self._max_consecutive_timeout_cycles = 3
        self._timeout_ratio_reconnect_threshold = 0.5
        self._last_successful_read = None
        self._last_failed_read = None
        self._last_block_timeout_time = None
        self._last_block_timeout_registers = None
        self._last_block_timeout_count = None
        self._last_block_timeout_keys = None
        self._last_block_read_duration = None
        self._last_cycle_stats = {
            "attempted_reads": 0,
            "successful_reads": 0,
            "timeout_reads": 0,
            "degraded": False,
            "last_cycle_at": None,
        }
        self._register_failures: dict[str, int] = {}
        self._last_attempt_times: dict = {}

        options = entry.options or {}
        self._update_scan_intervals(options)

        super().__init__(
            hass,
            _LOGGER,
            name="DynessCoordinator",
            update_interval=self.update_interval,
        )

        _LOGGER.debug("Coordinator initialized with update_interval: %s", self.update_interval)

    def _update_scan_intervals(self, options: dict):
        """Update scan intervals from config options."""
        self.scan_intervals = DEFAULT_SCAN_INTERVALS.copy()
        normalized_options = dict(options)
        if "high" not in normalized_options and "medium" in normalized_options:
            normalized_options["high"] = normalized_options["medium"]
        if "low" not in normalized_options and "very_low" in normalized_options:
            normalized_options["low"] = normalized_options["very_low"]

        for key in DEFAULT_SCAN_INTERVALS:
            if key in normalized_options:
                try:
                    self.scan_intervals[key] = int(normalized_options[key])
                except Exception:
                    _LOGGER.warning("Invalid scan interval for %s: %s", key, normalized_options[key])

        min_interval = min(self.scan_intervals.values()) if self.scan_intervals else 30
        self.update_interval = timedelta(seconds=min_interval)

        if hasattr(self, "_listeners") and self._listeners is not None:
            try:
                super(DynessCoordinator, self.__class__).update_interval.fset(self, self.update_interval)
            except Exception as e:
                _LOGGER.warning("Failed to update coordinator update_interval: %s", e)

        _LOGGER.debug(
            "Scan intervals updated. New: %s, Coordinator update_interval: %s",
            self.scan_intervals,
            self.update_interval,
        )

    @staticmethod
    def _definition_register_count(definition: dict) -> int:
        """Return the register span needed for a definition."""
        if definition.get("count") is not None:
            return int(definition["count"])
        data_type = definition.get("data_type", "uint16")
        if data_type in {"int32", "uint32"}:
            return 2
        if data_type == "schedule":
            return 5
        return 1

    def _block_read_timeout(self, block_count: int) -> float:
        """Return a dynamic timeout for block reads based on request size."""
        return min(10.0 + 0.15 * block_count, 22.0)

    def _build_contiguous_read_groups(self, sensors: list[dict]) -> list[list[dict]]:
        """Group sensor definitions into strictly contiguous register blocks."""
        if not sensors:
            return []
        ordered = sorted(sensors, key=lambda definition: definition["register"])
        groups: list[list[dict]] = []
        current_group: list[dict] = []
        current_end: int | None = None
        for sensor in ordered:
            register = sensor["register"]
            span = self._definition_register_count(sensor)
            sensor_end = register + span - 1
            if not current_group:
                current_group = [sensor]
                current_end = sensor_end
                continue
            if current_end is not None and register == current_end + 1 and sensor_end - current_group[0]["register"] < 125:
                current_group.append(sensor)
                current_end = sensor_end
                continue
            groups.append(current_group)
            current_group = [sensor]
            current_end = sensor_end
        if current_group:
            groups.append(current_group)
        return groups

    @staticmethod
    def _definitions_by_key(definitions: list[dict]) -> dict[str, dict]:
        return {definition["key"]: definition for definition in definitions}

    def _get_definition_for_key(self, key: str) -> dict | None:
        for definitions in (self.NUMBER_DEFINITIONS, self.SELECT_DEFINITIONS, self.SWITCH_DEFINITIONS):
            for definition in definitions:
                if definition.get("key") == key:
                    return definition
        return None

    def _get_post_write_refresh_targets(self, key: str) -> list[str]:
        if not key:
            return []
        definition = self._get_definition_for_key(key)
        if not definition:
            return []
        affects = definition.get("affects", [])
        if isinstance(affects, str):
            return [affects] if affects else []
        if isinstance(affects, (list, tuple, set)):
            return [str(item) for item in affects if str(item).strip()]
        return []

    def _cancel_pending_post_write_refresh(self) -> None:
        task = getattr(self, "_post_write_refresh_task", None)
        if task is not None and not task.done():
            task.cancel()
        self._post_write_refresh_task = None

    def _schedule_post_write_refresh(self, key: str) -> None:
        targets = self._get_post_write_refresh_targets(key)
        if not targets:
            return
        self._cancel_pending_post_write_refresh()
        self._post_write_refresh_task = self.hass.async_create_task(
            self._async_refresh_affected_keys_after_write(key, targets)
        )

    async def _async_refresh_affected_keys_after_write(self, key: str, targets: list[str]) -> None:
        if not targets:
            return
        for attempt in range(5):
            if attempt == 0:
                await asyncio.sleep(3.5)
            else:
                await asyncio.sleep(0.5)
            for target in targets:
                definition = self._get_definition_for_key(target)
                if not definition:
                    continue
                value = await self.async_read_value(definition, target, track_failure=False)
                if value is not None:
                    if not isinstance(self.data, dict):
                        self.data = {}
                    previous_value = self.data.get(target)
                    self.data[target] = value
                    self.async_set_updated_data(self.data)
                    if previous_value != value:
                        _LOGGER.debug(
                            "Post-write refresh updated '%s' after write to '%s' to %s",
                            target, key, value,
                        )
                        return

    def register_entity_type(self, key: str, entity_type: str):
        self._entity_types[key] = entity_type
        definition = next((d for d in self.SENSOR_DEFINITIONS if d.get("key") == key), None)
        if definition and "dependency_keys" in definition:
            for dep_alias, dep_key in definition["dependency_keys"].items():
                if dep_key not in self._entity_types:
                    self._entity_types[dep_key] = entity_type
                dep_def = next((d for d in self.SENSOR_DEFINITIONS if d.get("key") == dep_key), None)
                if dep_def:
                    scale = dep_def.get("scale")
                    if scale is not None:
                        self._scales[dep_key] = scale

    def get_connection_diagnostics(self) -> dict:
        from homeassistant.util.dt import utcnow
        now = utcnow()
        diagnostics = {
            "host": self.host,
            "port": self.port,
            "consecutive_failures": self._consecutive_failures,
            "connection_suspended": self._connection_suspended,
            "last_successful_read": self._last_successful_read.isoformat() if self._last_successful_read else None,
        }
        if self._connection_suspended and self._suspension_reset_time:
            diagnostics["suspension_expires_in_seconds"] = (self._suspension_reset_time - now).total_seconds()
        return diagnostics

    def get_connection_health_threshold_seconds(self) -> int:
        min_interval = min(self.scan_intervals.values()) if self.scan_intervals else 30
        return max(int(min_interval) * 3, 60)

    def is_connection_healthy(self) -> bool:
        from homeassistant.util.dt import utcnow
        if self._connection_suspended or self._last_successful_read is None:
            return False
        age_seconds = (utcnow() - self._last_successful_read).total_seconds()
        return age_seconds <= self.get_connection_health_threshold_seconds()

    def is_connection_degraded(self) -> bool:
        stats = self._last_cycle_stats or {}
        attempted_reads = int(stats.get("attempted_reads", 0) or 0)
        successful_reads = int(stats.get("successful_reads", 0) or 0)
        timeout_reads = int(stats.get("timeout_reads", 0) or 0)
        return successful_reads > 0 and (
            successful_reads < attempted_reads
            or timeout_reads > 0
            or self._consecutive_timeout_cycles > 0
        )

    def get_connection_health_attributes(self) -> dict:
        stats = self._last_cycle_stats or {}
        health = "offline"
        if self.is_connection_healthy():
            health = "degraded" if self.is_connection_degraded() else "ok"
        return {
            "health": health,
            "degraded": self.is_connection_degraded(),
            "last_successful_read": self._last_successful_read.isoformat() if self._last_successful_read else None,
            "last_failed_read": self._last_failed_read.isoformat() if self._last_failed_read else None,
            "last_block_timeout_time": self._last_block_timeout_time.isoformat() if self._last_block_timeout_time else None,
            "last_block_timeout_registers": self._last_block_timeout_registers,
            "last_block_timeout_count": self._last_block_timeout_count,
            "last_block_timeout_keys": self._last_block_timeout_keys,
            "last_block_read_duration": self._last_block_read_duration,
            "attempted_reads": int(stats.get("attempted_reads", 0) or 0),
            "successful_reads": int(stats.get("successful_reads", 0) or 0),
            "timeout_reads": int(stats.get("timeout_reads", 0) or 0),
            "consecutive_failures": self._consecutive_failures,
            "consecutive_timeout_cycles": self._consecutive_timeout_cycles,
            "connection_suspended": self._connection_suspended,
            "stale_after_seconds": self.get_connection_health_threshold_seconds(),
        }

    async def async_load_registers(self, version: str | None = None):
        """Load register definitions from YAML and populate coordinator attributes."""
        import yaml
        try:
            yaml_path = Path(__file__).parent / "registers" / "dyness.yaml"
            data = await self.hass.async_add_executor_job(
                lambda: yaml.safe_load(yaml_path.read_text())
            )
            # Normalize mapping-based sections into list-of-dicts format
            def _normalize_section(section):
                if isinstance(section, dict):
                    normalized = []
                    for key, value in section.items():
                        entry = dict(value or {})
                        entry.setdefault("key", key)
                        normalized.append(entry)
                    return normalized
                if isinstance(section, list):
                    return section
                return []

            self.SENSOR_DEFINITIONS = _normalize_section(data.get("SENSOR_DEFINITIONS", []))
            self.BINARY_SENSOR_DEFINITIONS = _normalize_section(data.get("BINARY_SENSOR_DEFINITIONS", []))
            self.SELECT_DEFINITIONS = _normalize_section(data.get("SELECT_DEFINITIONS", []))
            self.SWITCH_DEFINITIONS = _normalize_section(data.get("SWITCH_DEFINITIONS", []))
            self.NUMBER_DEFINITIONS = _normalize_section(data.get("NUMBER_DEFINITIONS", []))
            self.BUTTON_DEFINITIONS = _normalize_section(data.get("BUTTON_DEFINITIONS", []))
            self.EFFICIENCY_SENSOR_DEFINITIONS = _normalize_section(data.get("EFFICIENCY_SENSOR_DEFINITIONS", []))
            self.SOLAR_POWER_SENSOR_DEFINITIONS = _normalize_section(data.get("SOLAR_POWER_SENSOR_DEFINITIONS", []))
            self.VERSION_SENSOR_DEFINITIONS = _normalize_section(data.get("VERSION_SENSOR_DEFINITIONS", []))
            self.STORED_ENERGY_SENSOR_DEFINITIONS = _normalize_section(data.get("STORED_ENERGY_SENSOR_DEFINITIONS", []))
            self.CYCLE_SENSOR_DEFINITIONS = _normalize_section(data.get("CYCLE_SENSOR_DEFINITIONS", []))

            self._all_definitions = (
                self.SENSOR_DEFINITIONS
                + self.BINARY_SENSOR_DEFINITIONS
                + self.SELECT_DEFINITIONS
                + self.NUMBER_DEFINITIONS
                + self.SWITCH_DEFINITIONS
            )
            _LOGGER.debug("Loaded register definitions (%d entries)", len(self._all_definitions))
        except Exception as e:
            _LOGGER.warning("Failed to load register definitions: %s", e)
            self._all_definitions = []

    async def async_read_value(self, sensor: dict, key: str, track_failure: bool = True):
        """Helper to read a single sensor value from Modbus."""
        entity_type = self._entity_types.get(key, get_entity_type(sensor))
        scale = self._scales.get(key, sensor.get("scale", 1))
        unit = sensor.get("unit", "N/A")

        if not hasattr(self, "client") or self.client is None:
            _LOGGER.error("Modbus client is not available when reading %s '%s'", entity_type, key)
            return None

        try:
            value = await asyncio.wait_for(
                self.client.async_read_register(
                    register=sensor["register"],
                    data_type=sensor.get("data_type", "uint16"),
                    count=sensor.get("count"),
                    sensor_key=key,
                ),
                timeout=10.0,
            )
            if isinstance(value, (int, float, bool, str, dict, list)):
                _LOGGER.debug(
                    "Updated %s '%s' from single read: register=%d, value=%s, scale=%s, unit=%s",
                    entity_type, key, sensor["register"], value, scale, unit,
                )
                return value
            _LOGGER.warning("Invalid value for %s '%s': %r (type %s)", entity_type, key, value, type(value).__name__)
            return None
        except asyncio.TimeoutError:
            if track_failure:
                self._timeouts_in_cycle = getattr(self, "_timeouts_in_cycle", 0) + 1
            from homeassistant.util.dt import utcnow
            self._last_failed_read = utcnow()
            _LOGGER.warning("Timeout reading %s '%s' at register %d", entity_type, key, sensor["register"])
            return None
        except Exception as e:
            _LOGGER.error("Error reading %s '%s' at register %d: %s", entity_type, key, sensor["register"], e)
            return None

    async def _async_read_contiguous_group(self, block_sensors: list[dict], due_sensors: list[dict]) -> tuple[dict, dict]:
        if not block_sensors or not due_sensors:
            return {}, {"requests": 0, "block_requests": 0, "single_requests": 0, "failover_single_requests": 0}
        if len(block_sensors) == 1 and len(due_sensors) == 1:
            sensor = due_sensors[0]
            key = sensor["key"]
            value = await self.async_read_value(sensor, key)
            values = {key: value} if value is not None else {}
            return values, {"requests": 1, "block_requests": 0, "single_requests": 1, "failover_single_requests": 0}

        block_start = min(sensor["register"] for sensor in due_sensors)
        block_end = max(sensor["register"] + self._definition_register_count(sensor) - 1 for sensor in due_sensors)
        block_count = block_end - block_start + 1
        sensor_keys = ",".join(sensor["key"] for sensor in due_sensors)

        block_registers = None
        block_timeout_occurred = False
        block_start_time = perf_counter()
        try:
            block_registers = await asyncio.wait_for(
                self.client.async_read_holding_registers(
                    register=block_start,
                    count=block_count,
                    sensor_key=f"block[{sensor_keys}]",
                    max_retries=1,
                ),
                timeout=self._block_read_timeout(block_count),
            )
            self._last_block_read_duration = perf_counter() - block_start_time
        except asyncio.TimeoutError:
            block_timeout_occurred = True
            from homeassistant.util.dt import utcnow
            self._last_block_timeout_time = utcnow()
            self._last_block_timeout_registers = (block_start, block_end)
            self._last_block_timeout_count = block_count
            self._last_block_timeout_keys = sensor_keys
            self._last_block_read_duration = perf_counter() - block_start_time
            self._timeouts_in_cycle = getattr(self, "_timeouts_in_cycle", 0) + 1
            _LOGGER.warning("Block read timeout for registers %d-%d, falling back", block_start, block_end)
        except Exception as exc:
            from homeassistant.util.dt import utcnow
            self._last_failed_read = utcnow()
            _LOGGER.error("Unexpected error during block read for %d-%d: %s", block_start, block_end, exc)

        if block_registers is None:
            _LOGGER.debug("Contiguous block read failed for %d-%d; falling back", block_start, block_end)
            values: dict = {}
            for sensor in due_sensors:
                key = sensor["key"]
                value = await self.async_read_value(sensor, key)
                if value is not None:
                    values[key] = value
            return values, {
                "requests": 1 + len(due_sensors),
                "block_requests": 1,
                "single_requests": len(due_sensors),
                "failover_single_requests": len(due_sensors),
            }

        values: dict = {}
        for sensor in due_sensors:
            key = sensor["key"]
            register = sensor["register"]
            offset = register - block_start
            span = self._definition_register_count(sensor)
            raw_regs = block_registers[offset:offset + span]
            entity_type = self._entity_types.get(key, get_entity_type(sensor))
            scale = self._scales.get(key, sensor.get("scale", 1))
            unit = sensor.get("unit", "N/A")
            try:
                value = self.client._decode_registers(
                    register=register,
                    regs=raw_regs,
                    data_type=sensor.get("data_type", "uint16"),
                    bit_index=sensor.get("bit_index"),
                )
            except Exception as exc:
                _LOGGER.debug("Failed to decode block value for %s: %s", key, exc)
                value = None
            if value is not None:
                values[key] = value
                _LOGGER.debug("Updated %s '%s' from block read: register=%d, value=%s", entity_type, key, register, value)

        return values, {"requests": 1, "block_requests": 1, "single_requests": 0, "failover_single_requests": 0}

    async def async_write_value(self, register: int, value: int, key: str, scale=None, unit=None, entity_type="unknown"):
        """Write a value to a Modbus register asynchronously."""
        if not hasattr(self, "client") or self.client is None:
            _LOGGER.error("Modbus client is not available when writing %s '%s'", entity_type, key)
            return False

        _LOGGER.debug("Writing to %s '%s': register=%d, value=%s", entity_type, key, register, value)

        data_type = None
        try:
            defn = next((d for d in self.NUMBER_DEFINITIONS if d.get("key") == key), None)
            if not defn:
                defn = next((d for d in self.SWITCH_DEFINITIONS if d.get("key") == key), None)
            if defn:
                data_type = defn.get("data_type")
        except Exception:
            data_type = None

        if not data_type:
            data_type = "uint16"

        value_to_send = None
        if data_type == "int16":
            if not isinstance(value, int):
                _LOGGER.error("Value for %s '%s' must be int for int16", entity_type, key)
                return False
            value_to_send = value & 0xFFFF
        elif data_type == "uint16":
            if not isinstance(value, int) or not (0 <= value <= 0xFFFF):
                _LOGGER.error("Value for %s '%s' must be 0..65535 for uint16", entity_type, key)
                return False
            value_to_send = value
        else:
            _LOGGER.error("Unsupported data_type '%s' for key '%s' on write", data_type, key)
            return False

        try:
            import asyncio as _asyncio
            try:
                success = await _asyncio.wait_for(
                    self.client.async_write_register(register=register, value=value_to_send),
                    timeout=10.0,
                )
            except _asyncio.TimeoutError:
                _LOGGER.error("Timeout writing to register 0x%X for %s '%s'", register, entity_type, key)
                return False

            if success:
                _LOGGER.debug("Successfully wrote to %s '%s': register=%d, value=%s", entity_type, key, register, value_to_send)
                from homeassistant.util.dt import utcnow as _utcnow
                self._last_write_times[key] = _utcnow()
                self._schedule_post_write_refresh(key)
                return True
            else:
                _LOGGER.warning("Write operation failed for %s '%s': register=%d, value=%s", entity_type, key, register, value)
                return False
        except Exception as e:
            _LOGGER.error("Failed to write value %s to register 0x%X for %s '%s': %s", value, register, entity_type, key, e)
            return False

    async def _async_update_data(self):
        """Update all sensors asynchronously with per-sensor interval skipping."""
        from homeassistant.util.dt import utcnow
        from homeassistant.helpers import entity_registry as er

        now = utcnow()
        updated_data = {}
        attempted_reads = 0
        successful_reads = 0
        self._timeouts_in_cycle = 0

        if self._connection_suspended:
            if self._suspension_reset_time and now > self._suspension_reset_time:
                _LOGGER.info("Connection suspension expired - retrying")
                self._connection_suspended = False
                self._consecutive_failures = 0
            else:
                _LOGGER.debug("Connection suspended - skipping update")
                return self.data or {}

        _LOGGER.debug("Coordinator poll tick at %s", now.isoformat())

        entity_registry = er.async_get(self.hass)

        all_definitions_for_deps = (
            self.EFFICIENCY_SENSOR_DEFINITIONS
            + self.VERSION_SENSOR_DEFINITIONS
            + self.STORED_ENERGY_SENSOR_DEFINITIONS
            + self.CYCLE_SENSOR_DEFINITIONS
        )
        dependency_keys_set = {
            dep_key
            for defn in all_definitions_for_deps
            for dep_key in defn.get("dependency_keys", {}).values()
            if dep_key
        }

        due_sensors: list[dict] = []
        readable_sensors: list[dict] = []
        grouped_blocks = 0
        top_level_requests = 0
        block_requests = 0
        single_requests = 0
        failover_single_requests = 0

        for sensor in self._all_definitions:
            key = sensor["key"]
            entity_type = self._entity_types.get(key, get_entity_type(sensor))
            unique_id = f"{self.config_entry.entry_id}_{sensor['key']}"
            registry_entry = entity_registry.async_get_entity_id(entity_type, self.config_entry.domain, unique_id)
            is_disabled = False
            entry = entity_registry.entities.get(registry_entry) if registry_entry else None
            if entry:
                is_disabled = entry.disabled or entry.disabled_by is not None

            is_dependency = key in dependency_keys_set
            if is_disabled:
                if is_dependency:
                    _LOGGER.debug("Fetching disabled dependency key '%s'", key)
                else:
                    _LOGGER.debug("Skipping disabled entity '%s'", sensor.get("name", key))
                    continue

            readable_sensors.append(sensor)

            interval_name = sensor.get("scan_interval")
            interval = None
            if interval_name:
                interval = self.scan_intervals.get(interval_name)

            if interval is None:
                _LOGGER.warning("%s '%s' has no scan_interval defined, skipping", entity_type, key)
                continue

            last_write = self._last_write_times.get(key)
            if last_write is not None and (now - last_write).total_seconds() < 3:
                _LOGGER.debug("Suppressing read of '%s' after recent write", key)
                continue

            failures = self._register_failures.get(key, 0)
            backoff = min(2 ** failures, 64)
            effective_interval = min(interval * backoff, 3600)
            last_attempt = self._last_attempt_times.get(key)
            elapsed = (now - last_attempt).total_seconds() if last_attempt else None

            if elapsed is not None and elapsed < effective_interval:
                _LOGGER.debug("Skipping %s '%s', last attempt %.1fs ago", entity_type, key, elapsed)
                continue

            due_sensors.append(sensor)

        due_by_key = self._definitions_by_key(due_sensors)

        for block_group in self._build_contiguous_read_groups(readable_sensors):
            group_due_sensors = [sensor for sensor in block_group if sensor["key"] in due_by_key]
            if not group_due_sensors:
                continue
            grouped_blocks += 1
            group_values, group_stats = await self._async_read_contiguous_group(block_group, group_due_sensors)
            top_level_requests += group_stats["requests"]
            block_requests += group_stats["block_requests"]
            single_requests += group_stats["single_requests"]
            failover_single_requests += group_stats["failover_single_requests"]

            for sensor in group_due_sensors:
                key = sensor["key"]
                entity_type = self._entity_types.get(key, get_entity_type(sensor))
                interval_name = sensor.get("scan_interval")
                interval = self.scan_intervals.get(interval_name) if interval_name else None

                attempted_reads += 1
                self._read_start_times[key] = now
                value = group_values.get(key)

                if value is not None:
                    if sensor.get("state_class") == "total_increasing" and isinstance(value, (int, float)):
                        allow_reset = "_daily_" in key or "_monthly_" in key
                        if not allow_reset:
                            previous_value = self.data.get(key) if isinstance(self.data, dict) else None
                            if isinstance(previous_value, (int, float)):
                                regression = value < previous_value
                                scale_glitch = (previous_value > 0 and 0.08 <= (value / previous_value) <= 0.12)
                                if regression or scale_glitch:
                                    reason = "regression" if regression else "possible 10x scaling glitch"
                                    _LOGGER.warning("Ignoring suspicious %s for '%s' (new=%s, previous=%s)", reason, key, value, previous_value)
                                    self._last_attempt_times[key] = now
                                    continue

                    if sensor.get("data_type") == "schedule" and isinstance(value, dict):
                        try:
                            days = int(value.get("days") or 0)
                        except Exception:
                            days = value.get("days")
                        try:
                            start = int(value.get("start") or 0)
                        except Exception:
                            start = value.get("start")
                        try:
                            end = int(value.get("end") or 0)
                        except Exception:
                            end = value.get("end")
                        try:
                            enabled = int(value.get("enabled") or 0)
                        except Exception:
                            enabled = value.get("enabled")
                        try:
                            mode_signed = int(value.get("mode") or 0)
                            mode_raw = mode_signed & 0xFFFF
                        except Exception:
                            mode_raw = value.get("mode")
                        raw_regs = [days, start, end, mode_raw, enabled]
                        updated_data[key] = raw_regs
                        try:
                            updated_data[f"{key}_attrs"] = value
                        except Exception:
                            _LOGGER.exception("Failed to populate %s_attrs", key)
                    else:
                        updated_data[key] = value

                    self._last_update_times[key] = now
                    self._last_attempt_times[key] = now
                    prev_failures = self._register_failures.get(key, 0)
                    if prev_failures > 0:
                        _LOGGER.info("%s '%s' recovered after %d failure(s)", entity_type, key, prev_failures)
                    self._register_failures[key] = 0
                    successful_reads += 1
                else:
                    self._last_attempt_times[key] = now
                    new_failures = self._register_failures.get(key, 0) + 1
                    self._register_failures[key] = new_failures
                    next_backoff = min(2 ** new_failures, 64)
                    next_interval = min((interval or 30) * next_backoff, 3600)
                    if new_failures <= 3 or new_failures % 10 == 0:
                        _LOGGER.warning("Failed to read %s '%s' - value is None (failures: %d, next poll in %ds)", entity_type, key, new_failures, next_interval)

        degraded = successful_reads > 0 and (successful_reads < attempted_reads or self._timeouts_in_cycle > 0)

        if attempted_reads > 0:
            timeout_reads = int(getattr(self, "_timeouts_in_cycle", 0) or 0)
            if successful_reads > 0:
                if self._consecutive_failures > 0:
                    _LOGGER.info("Connection recovered after %d failures", self._consecutive_failures)
                self._consecutive_failures = 0
                self._connection_suspended = False
                self._last_successful_read = now
                if timeout_reads and (timeout_reads / attempted_reads) >= self._timeout_ratio_reconnect_threshold:
                    self._consecutive_timeout_cycles += 1
                    _LOGGER.warning("High timeout rate detected (%d/%d)", timeout_reads, attempted_reads)
                else:
                    self._consecutive_timeout_cycles = 0
                if self._consecutive_timeout_cycles >= self._max_consecutive_timeout_cycles:
                    _LOGGER.info("Repeated Modbus timeouts; retrying on next request")
                    self._consecutive_timeout_cycles = 0
            elif successful_reads == 0:
                self._consecutive_failures += 1
                _LOGGER.warning("All read attempts failed (%d/%d) - failures: %d/%d", successful_reads, attempted_reads, self._consecutive_failures, self._max_consecutive_failures)
                if self._consecutive_failures >= self._max_consecutive_failures:
                    self._connection_suspended = True
                    self._suspension_reset_time = now + timedelta(minutes=1)
                    _LOGGER.error("Connection suspended after %d failures. Will retry in 1 minute.", self._consecutive_failures)
                self._consecutive_timeout_cycles = 0
        else:
            _LOGGER.debug("No sensors due for update in this cycle")

        _LOGGER.debug(
            "Polling summary: due=%d, groups=%d, requests=%d, block_requests=%d, single_requests=%d, failover=%d, successful=%d",
            len(due_sensors), grouped_blocks, top_level_requests, block_requests, single_requests, failover_single_requests, successful_reads,
        )
        self._last_cycle_stats = {
            "attempted_reads": attempted_reads,
            "successful_reads": successful_reads,
            "timeout_reads": int(getattr(self, "_timeouts_in_cycle", 0) or 0),
            "degraded": degraded,
            "last_cycle_at": now,
        }

        if self.data is None:
            self.data = {}

        for _k in list(updated_data.keys()):
            _read_start = self._read_start_times.get(_k)
            _last_write = self._last_write_times.get(_k)
            if _read_start and _last_write and _last_write > _read_start:
                _LOGGER.debug("Discarding stale read of '%s'", _k)
                del updated_data[_k]

        self.data.update(updated_data)
        return self.data

    @staticmethod
    def get_registers():
        """Return a dict with entity/register definitions for the Dyness Aquavolt."""
        import yaml
        from pathlib import Path
        yaml_path = Path(__file__).parent / "registers" / "dyness.yaml"
        data = yaml.safe_load(yaml_path.read_text())
        def _normalize_section(section):
            if isinstance(section, dict):
                normalized = []
                for key, value in section.items():
                    entry = dict(value or {})
                    entry.setdefault("key", key)
                    normalized.append(entry)
                return normalized
            if isinstance(section, list):
                return section
            return []
        return {
            "SENSOR_DEFINITIONS": _normalize_section(data.get("SENSOR_DEFINITIONS", [])),
            "BINARY_SENSOR_DEFINITIONS": _normalize_section(data.get("BINARY_SENSOR_DEFINITIONS", [])),
            "SELECT_DEFINITIONS": _normalize_section(data.get("SELECT_DEFINITIONS", [])),
            "SWITCH_DEFINITIONS": _normalize_section(data.get("SWITCH_DEFINITIONS", [])),
            "NUMBER_DEFINITIONS": _normalize_section(data.get("NUMBER_DEFINITIONS", [])),
            "BUTTON_DEFINITIONS": _normalize_section(data.get("BUTTON_DEFINITIONS", [])),
            "EFFICIENCY_SENSOR_DEFINITIONS": _normalize_section(data.get("EFFICIENCY_SENSOR_DEFINITIONS", [])),
            "SOLAR_POWER_SENSOR_DEFINITIONS": _normalize_section(data.get("SOLAR_POWER_SENSOR_DEFINITIONS", [])),
            "VERSION_SENSOR_DEFINITIONS": _normalize_section(data.get("VERSION_SENSOR_DEFINITIONS", [])),
            "STORED_ENERGY_SENSOR_DEFINITIONS": _normalize_section(data.get("STORED_ENERGY_SENSOR_DEFINITIONS", [])),
            "CYCLE_SENSOR_DEFINITIONS": _normalize_section(data.get("CYCLE_SENSOR_DEFINITIONS", [])),
        }
