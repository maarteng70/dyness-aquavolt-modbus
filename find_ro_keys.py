import json

with open('C:\\dev\\dyeness_av\\custom_components\\dyness_modbus\\translations\\en.json', 'r', encoding='utf-8') as f:
    t = json.load(f)

# Search all keys recursively for RO keys
def find_ro_keys(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'RO' in k or '_RO' in k:
                print(f'  {path}.{k}: {v.get("name", "NO NAME") if isinstance(v, dict) else v}')
            find_ro_keys(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_ro_keys(v, f'{path}[{i}]')

print('Searching for RO keys in entire JSON...')
find_ro_keys(t)