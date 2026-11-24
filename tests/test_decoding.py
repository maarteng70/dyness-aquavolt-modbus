"""Tests for Dyness Aquavolt Modbus register decoding.

Tests the Modbus register decoding logic used by
DynessModbusClient._decode_registers (helpers/modbus_client.py).

NOTE ON TESTABILITY:
DynessModbusClient._decode_registers is a @staticmethod, but importing
custom_components.dyness_modbus.helpers.modbus_client triggers
custom_components/dyness_modbus/__init__.py, which imports
homeassistant.components.modbus. Home Assistant is not installed in this
test environment, so the real _decode_registers cannot be imported
directly without extensive mocking that breaks pytest internals.

To work around this, the decode logic from _decode_registers is
re-implemented below as decode_registers() and tested here. The logic
is identical to the production code. If Home Assistant becomes
installable, these tests should be rewritten to import and call
DynessModbusClient._decode_registers directly.

The "not available" sentinel is None, returned when register count is
insufficient for multi-register types.
"""

import pytest


# -----------------------------------------------------------------------
# Decode logic extracted from DynessModbusClient._decode_registers
# (helpers/modbus_client.py). Identical logic, standalone for testing.
# -----------------------------------------------------------------------

def decode_registers(register: int, regs: list[int], data_type: str = "uint16",
                     bit_index: int | None = None):
    """Decode raw holding registers into the requested data type."""
    if data_type == "int16":
        val = regs[0]
        return val - 0x10000 if val >= 0x8000 else val

    if data_type == "uint16":
        return regs[0]

    if data_type == "int32":
        if len(regs) < 2:
            return None
        val = (regs[0] << 16) | regs[1]
        return val - 0x100000000 if val >= 0x80000000 else val

    if data_type == "uint32":
        if len(regs) < 2:
            return None
        return (regs[0] << 16) | regs[1]

    if data_type == "uint64":
        val = 0
        for r in regs:
            val = (val << 16) | r
        return val

    if data_type == "char":
        byte_array = bytearray()
        for reg in regs:
            byte_array.append((reg >> 8) & 0xFF)
            byte_array.append(reg & 0xFF)
        null_pos = byte_array.find(0)
        if null_pos >= 0:
            byte_array = byte_array[:null_pos]
        return byte_array.decode("ascii", errors="ignore")

    if data_type == "mac":
        byte_array = bytearray()
        for reg in regs:
            byte_array.append((reg >> 8) & 0xFF)
            byte_array.append(reg & 0xFF)
        null_pos = byte_array.find(0)
        if null_pos >= 0:
            byte_array = byte_array[:null_pos]
        try:
            ascii_value = byte_array.decode("ascii", errors="strict").strip()
        except UnicodeDecodeError:
            ascii_value = ""
        if len(ascii_value) == 12 and all(c in "0123456789abcdefABCDEF" for c in ascii_value):
            return ":".join(ascii_value[index:index + 2].upper() for index in range(0, 12, 2))
        return ":".join(f"{byte:02X}" for byte in byte_array)

    if data_type == "schedule":
        if len(regs) < 5:
            return None
        mode_raw = int(regs[3])
        mode_signed = mode_raw - 0x10000 if mode_raw >= 0x8000 else mode_raw
        return {
            "days": int(regs[0]),
            "start": int(regs[1]),
            "end": int(regs[2]),
            "mode": mode_signed,
            "enabled": int(regs[4]),
        }

    if data_type == "bit":
        if bit_index is None or not (0 <= bit_index < 16):
            raise ValueError("bit_index must be between 0 and 15 for bit data_type")
        reg_val = regs[0]
        return bool((reg_val >> bit_index) & 1)

    raise ValueError(f"Unsupported data_type: {data_type}")


class TestDecodeRegisters:
    """Tests for the register decoding logic."""

    @pytest.mark.parametrize(
        "data_type,regs,expected",
        [
            # ----- uint16 (unsigned 16-bit) -----
            ("uint16", [0x0000], 0),
            ("uint16", [0x020B], 523),
            ("uint16", [0x7FFF], 32767),
            ("uint16", [0xFFFF], 65535),
            # ----- int16 (signed 16-bit) -----
            ("int16", [0x0000], 0),
            ("int16", [0x020B], 523),
            ("int16", [0x7FFF], 32767),
            ("int16", [0x8000], -32768),   # sign bit set -> negative
            ("int16", [0xFFFC], -4),
            ("int16", [0xFFFF], -1),
            # ----- uint32 (unsigned 32-bit, 2 registers, big-endian) -----
            ("uint32", [0x0000, 0x0001], 1),
            ("uint32", [0x0001, 0x0002], 65538),
            ("uint32", [0xFFFF, 0xFFFF], 4294967295),
            # ----- int32 (signed 32-bit, 2 registers, big-endian) -----
            ("int32", [0x0000, 0x0001], 1),
            ("int32", [0x0001, 0x0002], 65538),
            ("int32", [0x7FFF, 0xFFFF], 2147483647),
            ("int32", [0x8000, 0x0000], -2147483648),  # sign bit set
            ("int32", [0xFFFF, 0xFFFC], -4),
            ("int32", [0xFFFF, 0xFFFF], -1),
        ],
    )
    def test_decode_registers(self, data_type, regs, expected):
        """Raw registers decode to the expected Python value."""
        result = decode_registers(register=170, regs=regs, data_type=data_type)
        assert result == expected

    @pytest.mark.parametrize(
        "regs,bit_index,expected",
        [
            ([0x0001], 0, True),
            ([0x0001], 1, False),
            ([0x0002], 1, True),
            ([0x0002], 0, False),
            ([0x8000], 15, True),
            ([0x0000], 0, False),
        ],
    )
    def test_decode_bit(self, regs, bit_index, expected):
        """Bit data_type extracts a single bit from one register."""
        result = decode_registers(register=2002, regs=regs, data_type="bit",
                                  bit_index=bit_index)
        assert result == expected

    @pytest.mark.parametrize("data_type", ["int32", "uint32"])
    def test_decode_insufficient_registers_returns_none(self, data_type):
        """Multi-register types with too few registers return None (not available)."""
        result = decode_registers(register=120, regs=[0x0001], data_type=data_type)
        assert result is None

    def test_decode_unsupported_data_type_raises(self):
        """Unknown data_type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported data_type"):
            decode_registers(register=170, regs=[0x0001], data_type="float")

    # ------------------------------------------------------------------
    # NOT TESTABLE AS WRITTEN (listed per instructions)
    # -----------------------------------------------------------------------
    # - DynessModbusClient._decode_registers: cannot be imported because
    #   custom_components/dyness_modbus/__init__.py imports
    #   homeassistant.components.modbus, which is not installed in this
    #   environment. Mocking homeassistant breaks pytest's internal
    #   introspection. The decode logic above is copied verbatim from
    #   _decode_registers and tested here instead.
    #
    # - sensor.py DynessSensor.native_value applies scale/offset/precision
    #   and states mapping. It is a property that depends on
    #   coordinator.data and self.definition. Instantiating it requires a
    #   Home Assistant coordinator instance, so it is not directly
    #   unit-testable without mocking the coordinator. It is not tested
    #   here and has not been changed.
