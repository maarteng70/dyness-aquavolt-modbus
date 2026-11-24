import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    t = json.load(f)

# Navigate to the actual sensor translations
sensor_t = t['entity']['sensor']['sensor']
print('Total keys:', len(sensor_t))

# Check for RO keys
ro_keys = [k for k in sensor_t.keys() if 'RO' in k or '_RO' in k or 'ro' in k.lower()]
print('RO-like keys:', ro_keys)

# Check specific RO keys
for k in ['ems_power_mode_RO', 'operation_mode_RO', 'ems_power_set_RO', 'feed_power_para_RO', 
          'batt_charge_curr_max_RO', 'batt_discharge_curr_max_RO', 
          'router_ssid_RO', 'router_password_RO', 'router_encryption_RO', 'manufacturer_RO']:
    if k in sensor_t:
        print('FOUND:', k, '->', sensor_t[k].get('name', 'NO NAME'))
    else:
        print('MISSING:', k)

# Also check if they exist at the top level of sensor_t
print('\\nAll sensor keys containing RO:')
for k in sensor_t.keys():
    if 'RO' in k or '_RO' in k:
        print('  ', k)