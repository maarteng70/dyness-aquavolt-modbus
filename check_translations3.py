import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('"sensor":')
if start >= 0:
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
sensor_t = json.loads('{' + sensor_json + '}')
print('Keys in sensor:', list(sensor_t.keys()))