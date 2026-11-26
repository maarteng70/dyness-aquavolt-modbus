"""JSON validation tests for Dyness Aquavolt Modbus integration.

Tests that all JSON files in the project are valid JSON and can be parsed.
Also validates that all register definitions have corresponding translations.
"""

import json
import os
import pytest
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_json_files(root_dir: str) -> list[Path]:
    """Find all JSON files in the project."""
    json_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.json'):
                json_files.append(Path(root) / file)
    return json_files


def test_all_json_files_are_valid():
    """Test that all JSON files in the project are valid JSON."""
    project_root = Path(__file__).resolve().parents[1]
    json_files = find_json_files(str(project_root / "custom_components" / "dyness_modbus"))
    
    assert json_files, "No JSON files found in the integration"
    
    errors = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{json_file.relative_to(project_root)}: {e}")
        except UnicodeDecodeError as e:
            errors.append(f"{json_file.relative_to(project_root)}: Unicode decode error - {e}")
    
    if errors:
        pytest.fail(f"Invalid JSON files found:\n" + "\n".join(errors))


def test_translation_files_have_required_structure():
    """Test that translation files have the required structure."""
    project_root = Path(__file__).resolve().parents[1]
    translation_dir = project_root / "custom_components" / "dyness_modbus" / "translations"
    
    # At minimum, English translation must exist
    en_file = translation_dir / "en.json"
    assert en_file.exists(), "English translation file (en.json) is required"
    
    with open(en_file, 'r', encoding='utf-8') as f:
        t = json.load(f)
    
    # Check required top-level keys
    assert 'config' in t, "Missing 'config' section in translations"
    assert 'options' in t, "Missing 'options' section in translations"
    assert 'entity' in t, "Missing 'entity' section in translations"
    
    entity = t['entity']
    assert 'sensor' in entity, "Missing 'sensor' in entity translations"
    assert 'binary_sensor' in entity, "Missing 'binary_sensor' in entity translations"
    assert 'select' in entity, "Missing 'select' in entity translations"
    assert 'switch' in entity, "Missing 'switch' in entity translations"
    assert 'number' in entity, "Missing 'number' in entity translations"
    assert 'button' in entity, "Missing 'button' in entity translations"
    
    # Check for RO sensor translations
    sensor_t = entity['sensor']
    ro_keys = [k for k in sensor_t.keys() if 'RO' in k or '_RO' in k]
    assert ro_keys, "No RO sensor translations found"
    
    # Check specific RO keys exist
    required_ro_keys = [
        'ems_power_mode_RO',
        'operation_mode_RO',
        'ems_power_set_RO',
        'feed_power_para_RO',
        'batt_charge_curr_max_RO',
        'batt_discharge_curr_max_RO',
        'router_ssid_RO',
        'router_password_RO',
        'router_encryption_RO',
        'manufacturer_RO',
    ]
    for key in required_ro_keys:
        assert key in sensor_t, f"Missing required RO translation key: {key}"
        assert 'name' in sensor_t[key], f"Missing 'name' for {key}"
        if 'state' in sensor_t[key]:
            assert isinstance(sensor_t[key]['state'], dict), f"'state' for {key} must be a dict"


def test_all_register_definitions_have_translations():
    """Test that all register definitions in dyness.yaml have corresponding translations in en.json."""
    if yaml is None:
        pytest.skip("PyYAML not installed, skipping register translation test")

    project_root = Path(__file__).resolve().parents[1]
    yaml_file = project_root / "custom_components" / "dyness_modbus" / "registers" / "dyness.yaml"
    en_file = project_root / "custom_components" / "dyness_modbus" / "translations" / "en.json"

    assert yaml_file.exists(), f"Register definitions file not found: {yaml_file}"
    assert en_file.exists(), f"Translation file not found: {en_file}"

    # Load YAML register definitions
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)

    # Load translation file
    with open(en_file, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    entity_t = translations.get('entity', {})

    # Map YAML sections to translation sections
    section_mapping = {
        'SENSOR_DEFINITIONS': 'sensor',
        'BINARY_SENSOR_DEFINITIONS': 'binary_sensor',
        'SELECT_DEFINITIONS': 'select',
        'SWITCH_DEFINITIONS': 'switch',
        'NUMBER_DEFINITIONS': 'number',
        'BUTTON_DEFINITIONS': 'button',
    }

    errors = []

    for yaml_section, trans_section in section_mapping.items():
        definitions = yaml_data.get(yaml_section, {})
        if not isinstance(definitions, dict):
            continue

        trans_keys = entity_t.get(trans_section, {})
        if not isinstance(trans_keys, dict):
            errors.append(f"Missing translation section 'entity.{trans_section}' in en.json")
            continue

        for key, definition in definitions.items():
            if key not in trans_keys:
                reg = definition.get("register", "unknown")
                errors.append(f"Missing translation 'entity.{trans_section}.{key}' (register {reg})")

    if errors:
        pytest.fail(f"Register definitions missing translations:\n" + "\n".join(errors))


def test_no_orphan_translations():
    """Test that all translation keys correspond to existing register definitions."""
    if yaml is None:
        pytest.skip("PyYAML not installed, skipping orphan translation test")

    project_root = Path(__file__).resolve().parents[1]
    yaml_file = project_root / "custom_components" / "dyness_modbus" / "registers" / "dyness.yaml"
    en_file = project_root / "custom_components" / "dyness_modbus" / "translations" / "en.json"

    assert yaml_file.exists(), f"Register definitions file not found: {yaml_file}"
    assert en_file.exists(), f"Translation file not found: {en_file}"

    # Load YAML register definitions
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)

    # Load translation file
    with open(en_file, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    entity_t = translations.get('entity', {})

    # Collect all YAML definition keys per section
    yaml_keys_per_section = {}
    section_mapping = {
        'SENSOR_DEFINITIONS': 'sensor',
        'BINARY_SENSOR_DEFINITIONS': 'binary_sensor',
        'SELECT_DEFINITIONS': 'select',
        'SWITCH_DEFINITIONS': 'switch',
        'NUMBER_DEFINITIONS': 'number',
        'BUTTON_DEFINITIONS': 'button',
    }

    for yaml_section, trans_section in section_mapping.items():
        definitions = yaml_data.get(yaml_section, {})
        if isinstance(definitions, dict):
            yaml_keys_per_section[trans_section] = set(definitions.keys())
        else:
            yaml_keys_per_section[trans_section] = set()

    errors = []

    # Known computed sensors that don't have register definitions
    # These are derived from other sensors, not read from Modbus registers
    computed_sensor_keys = {
        'firmware_version',
        'round_trip_efficiency_total',
        'stored_energy',
        'solar_power_total',
        'battery_cycle_count_calc',
    }

    for trans_section, trans_keys in entity_t.items():
        if trans_section not in yaml_keys_per_section:
            # Unknown section in translations (e.g., "config" or "options" under entity)
            continue
        yaml_keys = yaml_keys_per_section[trans_section]
        if not isinstance(trans_keys, dict):
            continue
        for key in trans_keys:
            # Skip computed sensors that don't have register definitions
            if trans_section == 'sensor' and key in computed_sensor_keys:
                continue
            if key not in yaml_keys:
                errors.append(f"Orphan translation 'entity.{trans_section}.{key}' has no corresponding register definition")

    if errors:
        pytest.fail(f"Orphan translations found (no register definition):\n" + "\n".join(errors))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])