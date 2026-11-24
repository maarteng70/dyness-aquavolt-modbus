import yaml

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\registers\\dyness.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f.read())

sensor_defs = data['SENSOR_DEFINITIONS']
print('Type:', type(sensor_defs))
if isinstance(sensor_defs, dict):
    print('Keys:', list(sensor_defs.keys())[:10])
    # Check for scan_interval
    for k, v in list(sensor_defs.items())[:10]:
        print(f'  {k}: scan_interval={v.get("scan_interval")}')
    # Check specific entities
    for k in ['ac_port_power_total', 'ac_port_backup_power', 'utility_power_phase1', 'battery_power', 'battery_mode']:
        if k in sensor_defs:
            print(f'{k}: scan_interval={sensor_defs[k].get("scan_interval")}')
        else:
            print(f'{k}: NOT FOUND')