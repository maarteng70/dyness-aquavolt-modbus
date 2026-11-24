import yaml

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\registers\\dyness.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f.read())

print('Keys:', list(data.keys()))
for k in ['SENSOR_DEFINITIONS', 'BINARY_SENSOR_DEFINITIONS', 'SELECT_DEFINITIONS', 'SWITCH_DEFINITIONS', 'NUMBER_DEFINITIONS', 'BUTTON_DEFINITIONS']:
    if k in data:
        v = data[k]
        print(f'{k}: type={type(v).__name__}, len={len(v) if isinstance(v, list) else "N/A"}')
        if isinstance(v, list) and v:
            print(f'  First item keys: {list(v[0].keys()) if v else "empty"}')