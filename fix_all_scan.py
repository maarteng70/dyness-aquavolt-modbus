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

# Fix SENSOR_DEFINITIONS
sensor_defs = data['SENSOR_DEFINITIONS']
changes = 0
for k, v in sensor_defs.items():
    if v.get('scan_interval') == 'high':
        if k not in high_entities:
            v['scan_interval'] = 'medium'
            print(f"Changed {k} from high to medium")
    elif v.get('scan_interval') == 'medium':
        if k in high_entities:
            v['scan_interval'] = 'high'
            print(f"Fixed {k} from medium to high")

# Write back
with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\registers\\dyness.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    f.write('\n')

print('Done fixing scan intervals')