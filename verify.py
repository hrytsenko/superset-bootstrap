#!/usr/bin/env python3
"""Check that a running superset-bootstrap stack really works.

Start the stack first, then run this script:

    docker compose up -d --wait
    python verify.py

It fails with a non-zero exit code as soon as a check does not hold.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

SUPERSET_BASE_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088').rstrip('/')
SUPERSET_ENV_FILE = Path(__file__).resolve().with_name('.env')


class Failure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


def read_env():
    env = {}
    for line in SUPERSET_ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env[key.strip()] = value.strip()
    return env


def request(path, token=None, payload=None):
    url = f'{SUPERSET_BASE_URL}{path}'
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data)
    req.add_header('Accept', 'application/json')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', 'replace')[:500]
        raise Failure(f'{path} returned HTTP {error.code}: {detail}') from None
    except urllib.error.URLError as error:
        raise Failure(f'{path} is unreachable: {error.reason}') from None


def listing(path, token):
    return json.loads(request(f'{path}?q=(page_size:100)', token))['result']


def check_health():
    print('==> Check health')
    body = request('/health').strip()
    require(body == 'OK', f'Superset is not healthy: {body}')


def login(env):
    print('==> Log in')
    body = json.loads(request('/api/v1/security/login', payload={
        'username': env['SA_USERNAME'],
        'password': env['SA_PASSWORD'],
        'provider': 'db',
    }))
    require('access_token' in body, 'Login failed')
    return body['access_token']


def check_database(token, env):
    print('==> Check database')
    databases = [item['database_name'] for item in listing('/api/v1/database/', token)]
    require(
        env['DATASET_DB'] in databases,
        f'Database {env["DATASET_DB"]} is missing, found {databases}'
    )


def check_dashboard(token):
    print('==> Check dashboard')
    require(listing('/api/v1/dashboard/', token), 'Dashboard not imported')


def check_charts(token):
    print('==> Check charts')
    charts = listing('/api/v1/chart/', token)
    require(charts, 'Chart not imported')
    for chart in charts:
        name = chart['slice_name']
        result = json.loads(request(f'/api/v1/chart/{chart["id"]}/data/', token))['result']
        rows = result[0]['rowcount'] if result else 0
        require(rows, f'Chart {name} has no data')


def main():
    env = read_env()
    try:
        check_health()
        token = login(env)
        check_database(token, env)
        check_dashboard(token)
        check_charts(token)
    except Failure as failure:
        print(f'\nFAILED: {failure}', file=sys.stderr)
        return 1
    print('\nPASSED.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
