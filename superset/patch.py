import os
import re
import zipfile

with zipfile.ZipFile('/bootstrap/dashboards.zip', 'r') as z:
    files = {name: z.read(name) for name in z.namelist()}

database_filename = next(
    name for name in files
    if '/databases/' in f'/{name}' and name.endswith('.yaml')
)

database_uri = os.environ['SUPERSET_DATASET_DB_URI']
exported_content = files[database_filename].decode('utf-8')
patched_content = re.sub(
    r'(?m)^sqlalchemy_uri:.*$',
    f'sqlalchemy_uri: "{database_uri}"',
    exported_content
)
files[database_filename] = patched_content.encode('utf-8')

with zipfile.ZipFile('/tmp/dashboards.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)

print(f'Patched file: {database_filename}')
