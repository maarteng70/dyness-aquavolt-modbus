import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Try to parse the whole file
try:
    t = json.loads(content)
    print('Full JSON parses successfully')
except json.JSONDecodeError as e:
    print('JSON DECODE ERROR:', e)
    print('Error at position:', e.pos)
    print('Context:', content[max(0,e.pos-100):e.pos+100])