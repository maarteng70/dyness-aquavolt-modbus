import yaml

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\registers\\dyness.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f.read())

# The 5 entities that should be HIGH
high_entities = {
    'ac_port_power_total',
    'ac_port_backup_power',
    'utility_power_phase1',
    'battery_power',
    'battery_mode',
}

# Track changes
changes = 0

# Process all sections that have scan_interval
sections = [
    'SENSOR_DEFINITIONS',
    'BINARY_SENSOR_DEFINITIONS',
    'SELECT_DEFINITIONS',
    'SWITCH_DEFINITIONS',
    'NUMBER_DEFINITIONS',
    'BUTTON_DEFINITIONS',
    'EFFICIENCY_SENSOR_DEFINITIONS',
    'SOLAR_POWER_SENSOR_DEFINITIONS',
    'VERSION_SENSOR_DEFINITIONS',
    'STORED_ENERGY_SENSOR_DEFINITIONS',
    'CYCLE_SENSOR_DEFINITIONS',
]

for section_name in sections:
    if section_name in data and isinstance(data[section_name], list):
        for entry in data[section_name]:
            if isinstance(entry, dict) and entry.get('scan_interval') == 'high':
                key = entry.get('key')
                if key in high_entities:
                    # Keep as high
                    continue
                # Change to medium
                entry['scan_interval'] = 'medium'
                changes += 1
                print(f"Changed {entry.get('key', 'unknown')} from high to medium")

print(f"Total changes: {changes}")

# Write back
with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\registers\\dyness.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    f.write('\n')

print('Done')