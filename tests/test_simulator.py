"""Live-modbus simulator integration tests.

These tests are marked ``@pytest.mark.simulator`` and only run when
explicitly selected, e.g.::

    pytest -m simulator

They spin up a real pymodbus TCP server on localhost, populate its holding
registers from the register dump and the YAML register map, and drive the
real ``DynessModbusClient`` against it -- including a stop/restart reconnect
test.
"""

import asyncio
import importlib.machinery
import logging
import re
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusServerContext,
    ModbusSparseDataBlock,
)
from pymodbus.exceptions import ModbusException
from pymodbus.server import ModbusTcpServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _mock_module(name, **attrs):
    """Create a ModuleType with a proper __spec__ so pytest introspection works."""
    mod = ModuleType(name)
    mod.__spec__ = importlib.machinery.ModuleSpec(name, None)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# Mock homeassistant modules before importing the integration, because
# custom_components/dyness_modbus/__init__.py imports homeassistant which
# is not installed in this test environment.
_mock_module("homeassistant")
_mock_module("homeassistant.components")
_mock_module(
    "homeassistant.components.modbus", async_get_unit=MagicMock()
)
_mock_module("homeassistant.components.sensor", SensorEntity=MagicMock())
_mock_module(
    "homeassistant.config_entries", ConfigEntry=MagicMock()
)
_mock_module("homeassistant.core", HomeAssistant=MagicMock())
_mock_module("modbus_connection", ModbusTcpParams=MagicMock())
_mock_module("homeassistant.helpers.entity", Entity=MagicMock())
_mock_module(
    "homeassistant.helpers.update_coordinator", DataUpdateCoordinator=MagicMock()
)

from custom_components.dyness_modbus.const import DEFAULT_UNIT_ID
from custom_components.dyness_modbus.helpers.modbus_client import DynessModbusClient

logger = logging.getLogger(__name__)

SIMULATOR_HOST = "127.0.0.1"
SIMULATOR_PORT = 15020

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DUMP_PATH = PROJECT_ROOT / "mydevice" / "modbus_dump_20261121_140537.txt"

_LINE_RE = re.compile(
    r"^\s*(?P<addr>\d+)\s+\|.*?Raw:\s*(?P<raw>[0-9A-Fa-f]+(?:\s+[0-9A-Fa-f]+)*)\s*\|\s*Decoded:"
)


def load_dump_registers(path: Path) -> dict[int, int]:
    """Parse the modbus dump text file into {address: raw_value}.

    Every register that has a raw value in the dump is planted into the
    simulator image, so the real client can read it back exactly as the
    device reported it.
    """
    registers: dict[int, int] = {}
    for line in path.read_text().splitlines():
        m = _LINE_RE.match(line)
        if not m:
            continue
        addr = int(m.group("addr"))
        for i, word in enumerate(m.group("raw").split()):
            registers[addr + i] = int(word, 16)
    return registers


class SimUnit:
    """Minimal HA-ModbusUnit-like adapter over a pymodbus TCP client.

    Provides the async methods ``DynessModbusClient`` calls:
    ``read_holding_registers``, ``write_register``, plus ``set_message_spacing``.
    """

    def __init__(self, host: str, port: int, unit_id: int = DEFAULT_UNIT_ID):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self._client: AsyncModbusTcpClient | None = None

    async def _connect(self) -> None:
        if self._client is not None and self._client.connected:
            return
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
        self._client = AsyncModbusTcpClient(self.host, port=self.port)
        try:
            ok = await self._client.connect()
        except Exception:
            ok = False
        if not ok:
            raise OSError(f"connect failed to {self.host}:{self.port}")

    async def read_holding_registers(self, address: int, count: int):
        await self._connect()
        try:
            result = await self._client.read_holding_registers(
                address=address, count=count, device_id=self.unit_id
            )
        except Exception:
            return None
        if (
            result is None
            or isinstance(result, ModbusException)
            or getattr(result, "isError", lambda: False)()
        ):
            return None
        return list(result.registers)

    async def write_register(self, address: int, value: int) -> bool:
        await self._connect()
        try:
            await self._client.write_register(
                address=address, value=value, device_id=self.unit_id
            )
        except Exception:
            return False
        return True

    def set_message_spacing(self, seconds: float) -> None:
        """No-op pacing hook (the real HA unit throttles between messages)."""

    async def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None


class SimulatorHandle:
    """Handle to a running pymodbus TCP server that can be stopped/restarted."""

    def __init__(self, server, task, register_values: dict[int, int]):
        self.server = server
        self._task = task
        self._register_values = register_values
        self.host = SIMULATOR_HOST
        self.port = SIMULATOR_PORT
        self.unit_id = DEFAULT_UNIT_ID

    async def stop(self) -> None:
        await self.server.shutdown()
        await asyncio.gather(self._task, return_exceptions=True)

    async def start(self) -> None:
        block = ModbusSparseDataBlock(self._register_values)
        device = ModbusDeviceContext(hr=block)
        context = ModbusServerContext(devices=device, single=True)
        self.server = ModbusTcpServer(context, address=(self.host, self.port))
        self._task = asyncio.create_task(self.server.serve_forever())
        for _ in range(200):
            if self.server.is_active():
                return
            await asyncio.sleep(0.02)
        raise RuntimeError("simulator server did not restart")


async def _start_simulator(register_values: dict[int, int]) -> SimulatorHandle:
    block = ModbusSparseDataBlock(register_values)
    device = ModbusDeviceContext(hr=block)
    context = ModbusServerContext(devices=device, single=True)
    server = ModbusTcpServer(context, address=(SIMULATOR_HOST, SIMULATOR_PORT))
    task = asyncio.create_task(server.serve_forever())
    for _ in range(200):
        if server.is_active():
            break
        await asyncio.sleep(0.02)
    else:
        task.cancel()
        raise RuntimeError("simulator server did not become active")
    return SimulatorHandle(server, task, register_values)


@pytest.fixture
def register_values() -> dict[int, int]:
    """Register image built from the register dump."""
    return load_dump_registers(DUMP_PATH)


@pytest.fixture
async def simulator_server(register_values) -> SimulatorHandle:
    """Start a pymodbus TCP server on a local port; yield a restartable handle."""
    handle = await _start_simulator(register_values)
    try:
        yield handle
    finally:
        await handle.stop()


@pytest.fixture
async def simulator_unit(simulator_server: SimulatorHandle):
    """Yield a SimUnit adapter connected to the simulator."""
    unit = SimUnit(simulator_server.host, simulator_server.port, simulator_server.unit_id)
    yield unit
    await unit.close()


@pytest.fixture
async def simulator_client(simulator_unit: SimUnit):
    """Yield a real DynessModbusClient wired to the simulator unit."""
    client = DynessModbusClient(
        simulator_unit,
        simulator_unit.host,
        simulator_unit.port,
        message_wait_ms=0,
        unit_id=simulator_unit.unit_id,
    )
    yield client


@pytest.mark.simulator
async def test_read_registers_match_dump(simulator_client: DynessModbusClient):
    """Real client reads registers whose decoded values match the dump."""
    cases = [
        (0, "uint16", 238),            # Modbus protocol version
        (1, "uint16", 1590),           # Rated power
        (3, "char", "6LAC0512500W267240012", 11),  # Serial number
        (170, "uint16", 516),          # Battery1 Voltage
        (171, "int16", 325),           # Battery1 Current
        (172, "int16", 1677),          # Battery1 Power
        (213, "uint16", 35),           # Battery SOC
        (2010, "uint16", 35),          # SOC (BMS)
        (2011, "uint16", 100),         # BMS SOH
    ]
    for case in cases:
        register, data_type, expected = case[:3]
        count = case[3] if len(case) > 3 else None
        value = await simulator_client.async_read_register(
            register=register, data_type=data_type, count=count
        )
        assert value == expected, (
            f"register {register}: got {value!r}, expected {expected!r}"
        )


@pytest.mark.simulator
async def test_read_holding_registers_raw(simulator_client: DynessModbusClient):
    """Raw block read returns the values planted in the simulator."""
    regs = await simulator_client.async_read_holding_registers(register=170, count=3)
    assert regs == [516, 325, 1677]  # Battery1 V, I, P from dump


@pytest.mark.simulator
async def test_write_register(simulator_client: DynessModbusClient):
    """Write a register then read it back."""
    assert await simulator_client.async_write_register(register=27511, value=1) is True  # EMS Power Mode
    regs = await simulator_client.async_read_holding_registers(register=27511, count=1)
    assert regs == [1]


@pytest.mark.simulator
async def test_simulator_stop_start_reconnect(simulator_server: SimulatorHandle, simulator_client: DynessModbusClient):
    """Stop the simulator, restart it, verify the client reconnects and reads still work."""
    before = await simulator_client.async_read_holding_registers(register=213, count=1)
    assert before == [35]

    await simulator_server.stop()

    # While the server is down, reads should fail after retries.
    down = await simulator_client.async_read_holding_registers(register=213, count=1)
    assert down is None

    await simulator_server.start()

    # After restart the same client instance reconnects on the next request.
    after = await simulator_client.async_read_holding_registers(register=213, count=1)
    assert after == [35]
