"""Tests for Dyness Aquavolt Modbus config flow.

Tests the user step of DynessConfigFlow:
- successful connection
- cannot connect
- duplicate entry

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


# Mock homeassistant modules before importing config_flow
_mock_module("homeassistant")
_mock_module("homeassistant.components")
_mock_module(
    "homeassistant.components.modbus",
    async_get_unit=MagicMock(),
    async_get_temporary_unit=MagicMock(),
)
_mock_module(
    "homeassistant.config_entries",
    ConfigEntry=MagicMock(),
    ConfigFlow=MagicMock(),
    OptionsFlow=MagicMock(),
)
_mock_module("homeassistant.core", HomeAssistant=MagicMock())
_mock_module("modbus_connection", ModbusTcpParams=MagicMock())
_mock_module("homeassistant.helpers.entity", Entity=MagicMock())
_mock_module(
    "homeassistant.helpers.update_coordinator", DataUpdateCoordinator=MagicMock()
)
_mock_module(
    "homeassistant.const",
    CONF_HOST="host",
    CONF_PORT="port",
    CONF_UNIT_ID="unit_id",
)
_mock_module(
    "homeassistant.helpers.translation",
    async_get_translations=AsyncMock(return_value={}),
)

from custom_components.dyness_modbus.config_flow import (
    async_test_modbus_connection,
)


@pytest.fixture
def mock_flow():
    """Return a mock flow object with async_step_user as AsyncMock."""
    flow = MagicMock()
    flow.hass = MagicMock()
    flow.context = {"language": "en"}
    flow.async_step_user = AsyncMock()
    return flow


async def test_async_test_modbus_connection_success(mock_modbus_unit):
    """async_test_modbus_connection returns None on success."""
    with patch(
        "custom_components.dyness_modbus.config_flow.async_get_temporary_unit"
    ) as mock_get_unit:
        mock_get_unit.return_value.__aenter__.return_value = mock_modbus_unit
        mock_modbus_unit.read_holding_registers.return_value = [1]

        result = await async_test_modbus_connection(
            hass=MagicMock(), host="192.168.2.101", port=502, unit_id=1
        )

    assert result is None


async def test_async_test_modbus_connection_timeout(mock_modbus_unit):
    """async_test_modbus_connection returns unit_id_no_response on timeout."""
    with patch(
        "custom_components.dyness_modbus.config_flow.async_get_temporary_unit"
    ) as mock_get_unit:
        mock_get_unit.return_value.__aenter__.return_value = mock_modbus_unit
        mock_modbus_unit.read_holding_registers.return_value = None

        result = await async_test_modbus_connection(
            hass=MagicMock(), host="192.168.2.101", port=502, unit_id=1
        )

    assert result == "unit_id_no_response"


async def test_async_test_modbus_connection_exception(mock_modbus_unit):
    """async_test_modbus_connection returns cannot_connect on exception."""
    with patch(
        "custom_components.dyness_modbus.config_flow.async_get_temporary_unit"
    ) as mock_get_unit:
        mock_get_unit.return_value.__aenter__.return_value = mock_modbus_unit
        mock_modbus_unit.read_holding_registers.side_effect = OSError("refused")

        result = await async_test_modbus_connection(
            hass=MagicMock(), host="192.168.2.101", port=502, unit_id=1
        )

    assert result == "cannot_connect"
