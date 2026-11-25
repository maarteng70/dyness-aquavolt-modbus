"""JSON validation tests for Dyness Aquavolt Modbus integration.

Tests that all JSON files in the project are valid JSON and can be parsed.
"""

import json
import os
import pytest
from pathlib import Path


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])