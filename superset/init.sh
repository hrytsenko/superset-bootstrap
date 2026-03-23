#!/bin/bash
set -euo pipefail

echo '==> Migrate database'
superset db upgrade

echo '==> Create admin'
superset fab create-admin \
  --username "${SA_USERNAME}" --password "${SA_PASSWORD}" \
  --email "${SA_EMAIL}" --firstname "${SA_FIRSTNAME}" --lastname "${SA_LASTNAME}" \
  || true

echo '==> Init superset'
superset init

echo '==> Patch import'
python /bootstrap/patch.py

echo '==> Import dashboards'
superset import-dashboards -p /tmp/dashboards.zip -u "${SA_USERNAME}"
