import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    t = json.load(f)

print('Top-level keys:', list(t.keys()))
if 'entity' in t:
    print('entity keys:', list(t['entity'].keys()))
    if 'sensor' in t['entity']:
        print('entity.sensor keys:', list(t['entity']['sensor'].keys()))
        if 'sensor' in t['entity']['sensor']:
            print('entity.sensor.sensor keys:', list(t['entity']['sensor']['sensor'].keys())[:30])