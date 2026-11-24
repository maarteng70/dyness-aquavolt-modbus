import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import importlib.machinery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _mock_module(name, **attrs):
    """Create a ModuleType with a proper __spec__ so pytest introspection works."""
    mod = ModuleType(name)
    mod.__spec__ = importlib.machinery.ModuleSpec(name, None)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# Mock homeassistant modules before importing modbus_client, because
# custom_components/dyness_modbus/__init__.py imports homeassistant which
# is not installed in this test environment.
_mock_module("homeassistant")
_mock_module("homeassistant.components")
_mock_module("homeassistant.components.modbus", async_get_unit=MagicMock())
_mock_module(
    "homeassistant.config_entries", ConfigEntry=MagicMock()
)
_mock_module("homeassistant.core", HomeAssistant=MagicMock())
_mock_module("modbus_connection", ModbusTcpParams=MagicMock())
_mock_module("homeassistant.helpers.entity", Entity=MagicMock())
_mock_module(
    "homeassistant.helpers.update_coordinator", DataUpdateCoordinator=MagicMock()
)

from custom_components.dyness_modbus.helpers.modbus_client import DynessModbusClient


class FakeClient:
    def __init__(self):
        self.read_calls = 0
        self.read_kwargs = None
        self.write_calls = 0
        self.write_kwargs = None
        self.message_spacing = None

    def set_message_spacing(self, seconds):
        self.message_spacing = seconds

    async def read_holding_registers(self, address, count, **kwargs):
        self.read_calls += 1
        self.read_kwargs = kwargs
        return [1] * count

    async def write_register(self, address, value, **kwargs):
        self.write_calls += 1
        self.write_kwargs = kwargs
        return None


async def test_read_holding_registers_uses_shared_unit_return_value():
    fake_client = FakeClient()
    client = DynessModbusClient(
        fake_client, "127.0.0.1", 502, message_wait_ms=0
    )
    result = await client.async_read_holding_registers(register=1, count=1, max_retries=1, retry_delay=0)
    assert result == [1]
    assert fake_client.read_calls == 1
    assert fake_client.message_spacing == 0


async def test_write_register_uses_shared_unit_return_value():
    fake_client = FakeClient()
    client = DynessModbusClient(
        fake_client, "127.0.0.1", 502, message_wait_ms=0
    )
    result = await client.async_write_register(register=1, value=10, max_retries=1, retry_delay=0)
    assert result is True
    assert fake_client.write_calls == 1
    assert fake_client.write_kwargs == {}
