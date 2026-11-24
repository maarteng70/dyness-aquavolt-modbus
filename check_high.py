import yaml

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\registers\\dyness.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f.read())

sensor_defs = data['SENSOR_DEFINITIONS']
high_entities = {
    'ac_port_power_total',
    'ac_port_backup_power',
    'utility_power_phase1',
    'battery_power',
    'battery_mode',
}

high_count = 0
other_high = []
for k, v in sensor_defs.items():
    if v.get('scan_interval') == 'high':
        if k not in high_entities:
            print(f'OTHER HIGH: {k}')
        else:
            print(f'CORRECT HIGH: {k}')

print('Done checking')