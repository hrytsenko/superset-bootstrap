import os
import re
import zipfile
from urllib.parse import urlparse

with zipfile.ZipFile('/bootstrap/dashboards.zip', 'r') as z:
    files = {name: z.read(name) for name in z.namelist()}

database_uri = os.environ['SUPERSET_DATASET_DB_URI']
database_filename = next(
    name for name in files
    if '/databases/' in f'/{name}' and name.endswith('.yaml')
)
exported_content = files[database_filename].decode('utf-8')
patched_content = re.sub(
    r'(?m)^sqlalchemy_uri:.*$',
    f'sqlalchemy_uri: "{database_uri}"',
    exported_content
)
files[database_filename] = patched_content.encode('utf-8')
print(f'Patched file: {database_filename}')

database_name = urlparse(database_uri).path.lstrip('/')
dataset_filename = next(
    name for name in files
    if '/datasets/' in f'/{name}' and name.endswith('.yaml')
)
exported_content = files[dataset_filename].decode('utf-8')
patched_content = re.sub(
    r'(?m)^catalog:.*$',
    f'catalog: {database_name}',
    exported_content
)
files[dataset_filename] = patched_content.encode('utf-8')
print(f'Patched file: {dataset_filename}')

with zipfile.ZipFile('/tmp/dashboards.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)
