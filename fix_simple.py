import json

# Read current file
with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    t = json.load(f)

# The RO keys are currently in entity.number - move them to entity.sensor
# They should already be in entity.sensor after our edits, but let's verify
sensor_t = t['entity']['sensor']
number_t = t['entity']['number']

# RO keys that should be in sensor
ro_keys = [
    'ems_power_set_RO', 'ems_power_mode_RO', 'operation_mode_RO',
    'feed_power_para_RO', 'batt_charge_curr_max_RO', 'batt_discharge_curr_max_RO',
    'router_ssid_RO', 'router_password_RO', 'router_encryption_RO', 'manufacturer_RO'
]

# Check if they're in sensor
for k in [
    'ems_power_mode_RO', 'operation_mode_RO', 'ems_power_set_RO',
    'feed_power_para_RO', 'batt_charge_curr_max_RO', 'batt_discharge_curr_max_RO',
    'router_ssid_RO', 'router_password_RO', 'router_encryption_RO', 'manufacturer_RO'
]:
    if k in t['entity']['sensor']:
        print('FOUND in sensor:', k)
    else:
        print('MISSING from sensor:', k)

# Write back
with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'w', encoding='utf-8') as f:
    json.dump(t, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('Done')