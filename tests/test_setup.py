"""Trivial setup tests for Dyness Aquavolt Modbus integration."""

import os
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_manifest_has_domain():
    """Manifest domain must be set."""
    path = os.path.join(
        PROJECT_ROOT, "custom_components", "dyness_modbus", "manifest.json"
    )
    with open(path) as f:
        manifest = yaml.safe_load(f.read())
    assert manifest["domain"] == "dyness_modbus"
    assert manifest["name"] == "Dyness Aquavolt Modbus"


def test_yaml_registers_load():
    """Register YAML must load and contain expected keys."""
    path = os.path.join(
        PROJECT_ROOT,
        "custom_components",
        "dyness_modbus",
        "registers",
        "dyness.yaml",
    )
    with open(path) as f:
        data = yaml.safe_load(f.read())
    assert "SENSOR_DEFINITIONS" in data
    assert "SELECT_DEFINITIONS" in data
    assert "NUMBER_DEFINITIONS" in data
    # YAML uses mapping format: key name is the dict key
    assert "ems_power_mode" in data["SELECT_DEFINITIONS"]
    assert "ems_power_set" in data["NUMBER_DEFINITIONS"]
    assert "ems_power_set_RO" in data["SENSOR_DEFINITIONS"]
    assert "ems_power_mode_RO" in data["SENSOR_DEFINITIONS"]
    assert "operation_mode_RO" in data["SENSOR_DEFINITIONS"]


def test_mock_modbus_unit_read(mock_modbus_unit):
    """Mock Modbus unit can read registers."""
    import asyncio

    result = asyncio.run(mock_modbus_unit.read_holding_registers(address=170, count=1))
    assert result == [1] * 10


def test_mock_modbus_unit_write(mock_modbus_unit):
    """Mock Modbus unit can write registers."""
    import asyncio

    result = asyncio.run(mock_modbus_unit.write_register(address=25243, value=1))
    assert result is None
