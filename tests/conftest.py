"""Conftest for Dyness Aquavolt Modbus integration tests."""

import pytest
from unittest.mock import AsyncMock


class FakeModbusUnit:
    """Mock Modbus unit for testing."""

    def __init__(self):
        self.read_holding_registers = AsyncMock(return_value=[1] * 10)
        self.write_register = AsyncMock(return_value=None)
        self.message_spacing = None

    def set_message_spacing(self, seconds):
        self.message_spacing = seconds


@pytest.fixture
def mock_modbus_unit():
    """Return a mock Modbus TCP unit."""
    return FakeModbusUnit()
