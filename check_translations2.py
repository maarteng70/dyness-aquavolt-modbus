import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Find sensor section
start = content.find('"sensor":')
if start >= 0:
    # Find matching brace
    brace_count = 0
    end = start
    for i, ch in enumerate(content[start:], start):
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0:
                end = i + 1
                break
    
    sensor_json = content[start:end]
    print('Sensor section length:', len(sensor_json))
    
    try:
        sensor_t = json.loads('{' + sensor_json + '}')
        print('Parsed successfully!')
        print('Keys:', len(sensor_t))
        for k in ['ems_power_mode_RO', 'operation_mode_RO', 'ems_power_set_RO', 'feed_power_para_RO', 
                  'batt_charge_curr_max_RO', 'batt_discharge_curr_max_RO', 
                  'router_ssid_RO', 'router_password_RO', 'router_encryption_RO', 'manufacturer_RO']:
            if k in sensor_t:
                print('FOUND:', k, '->', sensor_t[k].get('name', 'NO NAME'))
            else:
                print('MISSING:', k)
    except json.JSONDecodeError as e:
        print('JSON decode error:', e)
        print('Error at pos:', e.pos)
        print('Context:', sensor_json[max(0,e.pos-50):e.pos+50])