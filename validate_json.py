import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Try to parse
try:
    t = json.loads(content)
    print('JSON is valid!')
except json.JSONDecodeError as e:
    print('JSON ERROR:', e)
    print('Position:', e.pos)
    print('Context:', content[max(0,e.pos-50):e.pos+100])