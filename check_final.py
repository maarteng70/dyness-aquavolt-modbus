import json
import re

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for duplicate keys
keys = re.findall(r'"([^"]+)"\s*:', content)
dupes = {k for k in keys if keys.count(k) > 1}
if dupes:
    print('Duplicate keys:', dupes)
else:
    print('No duplicate keys found')

# Also check the structure
import json
try:
    t = json.loads(content)
    print('JSON parses successfully!')
except json.JSONDecodeError as e:
    print('JSON Error:', e)
    print('Position:', e.pos)
    print('Line:', e.lineno, 'Col:', e.colno)