import re
with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    content = f.read()
for m in re.finditer(r'"(.*?_RO)"', content):
    print(m.group(1), 'at position', m.start())