# Superset Bootstrap

## Goals

1. Run Superset with minimal Docker setup.
2. Support export and import of dashboards.
3. Use external database for analytics data.

## Approaches

1. Extend Superset with required database driver.
2. Initialize Superset via a startup job.
3. Import dashboards during initialization.
4. Patch database URI in dashboards before import.

## Actions

After startup, open Superset at http://localhost:8088/.

Start:

```shell
docker compose up -d --wait
```

Stop:

```shell
docker compose down -v
```
