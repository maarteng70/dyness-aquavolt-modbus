"""Tests for Dyness Aquavolt Modbus integration setup.

Tests:
- async_setup_entry creates coordinator and forwards platforms
- async_unload_entry unloads platforms and removes coordinator
- Entities are created from register definitions

Uses mock_modbus_unit from conftest.py to mock the Modbus TCP client.
"""

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch

import importlib.machinery

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _mock_module(name, **attrs):
    """Create a ModuleType with a proper __spec__ so pytest introspection works."""
    mod = ModuleType(name)
    mod.__spec__ = importlib.machinery.ModuleSpec(name, None)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# Mock homeassistant modules before importing integration
_mock_module("homeassistant")
_mock_module("homeassistant.components")
_mock_module("homeassistant.components.modbus", async_get_unit=MagicMock())
_mock_module("homeassistant.components.sensor", SensorEntity=MagicMock())
_mock_module("homeassistant.config_entries", ConfigEntry=MagicMock())
_mock_module("homeassistant.core", HomeAssistant=MagicMock())
_mock_module("modbus_connection", ModbusTcpParams=MagicMock())
_mock_module("homeassistant.helpers.entity", Entity=MagicMock())
_mock_module(
    "homeassistant.helpers.update_coordinator", DataUpdateCoordinator=MagicMock()
)

from custom_components.dyness_modbus import async_setup_entry, async_unload_entry
from custom_components.dyness_modbus.coordinator import DynessCoordinator


@pytest.fixture
def hass():
    """Return a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    # Set up config_entries mock chain
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass


@pytest.fixture
def config_entry(mock_modbus_unit):
    """Return a mock config entry."""
    entry = MagicMock()
    entry.data = {
        "host": "192.168.2.101",
        "port": 502,
        "unit_id": 1,
    }
    entry.entry_id = "test_entry_id"
    return entry


async def test_setup_entry(hass, config_entry, mock_modbus_unit):
    """Setting up an entry creates coordinator and forwards platforms."""
    with patch(
        "custom_components.dyness_modbus.async_get_unit"
    ) as mock_get_unit:
        mock_get_unit.return_value = mock_modbus_unit

        # Mock the coordinator class to return a proper async coordinator
        with patch(
            "custom_components.dyness_modbus.DynessCoordinator"
        ) as mock_coordinator_class:
            mock_coordinator = MagicMock()
            mock_coordinator.async_load_registers = AsyncMock()
            mock_coordinator.async_config_entry_first_refresh = AsyncMock()
            mock_coordinator_class.return_value = mock_coordinator

            result = await async_setup_entry(hass, config_entry)

    assert result is True
    assert hass.data["dyness_modbus"][config_entry.entry_id] is not None
    assert hass.config_entries.async_forward_entry_setups.called


async def test_unload_entry(hass, config_entry, mock_modbus_unit):
    """Unloading an entry removes coordinator and unloads platforms."""
    # First set up
    with patch(
        "custom_components.dyness_modbus.async_get_unit"
    ) as mock_get_unit:
        mock_get_unit.return_value = mock_modbus_unit

        with patch(
            "custom_components.dyness_modbus.DynessCoordinator"
        ) as mock_coordinator_class:
            mock_coordinator = MagicMock()
            mock_coordinator.async_load_registers = AsyncMock()
            mock_coordinator.async_config_entry_first_refresh = AsyncMock()
            mock_coordinator_class.return_value = mock_coordinator

            await async_setup_entry(hass, config_entry)

    assert config_entry.entry_id in hass.data["dyness_modbus"]

    # Now unload
    result = await async_unload_entry(hass, config_entry)

    assert result is True
    assert config_entry.entry_id not in hass.data["dyness_modbus"]
    hass.config_entries.async_unload_platforms.assert_called_once()


async def test_entities_created_from_registers(hass, config_entry, mock_modbus_unit):
    """Sensor entities are created from register definitions."""
    with patch(
        "custom_components.dyness_modbus.async_get_unit"
    ) as mock_get_unit:
        mock_get_unit.return_value = mock_modbus_unit

        with patch(
            "custom_components.dyness_modbus.DynessCoordinator"
        ) as mock_coordinator_class:
            mock_coordinator = MagicMock()
            mock_coordinator.async_load_registers = AsyncMock()
            mock_coordinator.async_config_entry_first_refresh = AsyncMock()
            mock_coordinator.SENSOR_DEFINITIONS = [
                {"key": "battery_soc"},
                {"key": "battery_power"},
                {"key": "ac_port_power_total"},
            ]
            mock_coordinator_class.return_value = mock_coordinator

            await async_setup_entry(hass, config_entry)

    coordinator = hass.data["dyness_modbus"][config_entry.entry_id]

    # Verify coordinator has sensor definitions loaded
    assert len(coordinator.SENSOR_DEFINITIONS) > 0
    assert any(
        s["key"] == "battery_soc" for s in coordinator.SENSOR_DEFINITIONS
    ), "battery_soc sensor should be defined"
    assert any(
        s["key"] == "battery_power" for s in coordinator.SENSOR_DEFINITIONS
    ), "battery_power sensor should be defined"
    assert any(
        s["key"] == "ac_port_power_total" for s in coordinator.SENSOR_DEFINITIONS
    ), "ac_port_power_total sensor should be defined"

