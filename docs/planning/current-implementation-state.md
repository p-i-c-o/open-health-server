[Repo Home](../../README.md) / [Docs](../README.md) / [Planning](README.md) / Current Implementation State

# Current Implementation State

> This is the handoff document for any human or AI agent continuing implementation. It records what exists now, what has been verified, what is intentionally not implemented yet, and what should happen next.

## Summary

open-health-server has moved from planning-only docs into a minimal FastAPI backend with PostgreSQL/TimescaleDB infrastructure. Phase 0 is mostly complete, Phase 1 is complete, Phase 2 is complete, and Phase 3 is complete.

Current completed foundation:

- FastAPI backend skeleton exists.
- Local Python virtual environment `.venv/` exists and has dependencies installed.
- Docker Compose starts TimescaleDB/PostgreSQL.
- SQLAlchemy database helper exists.
- SQLAlchemy model metadata exists for Schema V1.
- Alembic migration system exists.
- First migration enables the TimescaleDB extension.
- Second migration creates Schema V1 tables, indexes, and the `samples` hypertable.
- Seed catalog command validates and upserts metric definitions.
- `/health` and `/version` routes exist.
- Unit tests pass.
- Alembic has been applied successfully against the Dockerized database.
- The implementation timeline has been converted into checkboxes and updated to reflect this state.

## Important Current Runtime State

During implementation, the TimescaleDB container was run and verified healthy:

```text
open-health-server-db-1
image: timescale/timescaledb:latest-pg16
host port: 5433
container port: 5432
status during verification: healthy
```

The host port is intentionally `5433` because `5432` was already in use on this machine.

At the end of the session, the DB container was stopped with `docker compose stop db` and the API dev server was not running. See [Session Handoff 2026-06-11](session-handoff-2026-06-11.md) for resume commands.

## Repository Layout

Important implementation files:

```text
pyproject.toml
.env.example
.gitignore
docker-compose.yml
alembic.ini
backend/
backend/app/
backend/app/main.py
backend/app/settings.py
backend/app/database.py
backend/app/models.py
backend/app/commands/seed_catalog.py
backend/app/routes/health.py
backend/app/routes/version.py
backend/migrations/
backend/migrations/env.py
backend/migrations/script.py.mako
backend/migrations/versions/20260611_0001_enable_timescaledb.py
backend/migrations/versions/20260611_0002_create_schema_v1_tables.py
tests/
tests/test_database.py
tests/test_system_routes.py
catalog/
catalog/seed-metric-catalog-v1.json
catalog/seed-metric-catalog-v1.md
docs/planning/implementation-timeline.md
docs/planning/schema-v1.md
docs/planning/metric-taxonomy-and-schema.md
```

Generated or local-only files/directories that should stay untracked:

```text
.venv/
__pycache__/
.pytest_cache/
open_health_server.egg-info/
.env
```

`.obsidian/` is also untracked and pre-existing/user-owned. Do not treat it as implementation work unless the user asks.

## Backend Stack

Chosen stack:

- Python 3.13 currently available locally.
- FastAPI for the HTTP API.
- Pydantic Settings for environment/config loading.
- SQLAlchemy 2.x for database access.
- psycopg 3 for PostgreSQL connectivity.
- Alembic for migrations.
- PostgreSQL with TimescaleDB through Docker Compose.
- Pytest for tests.

The package is installed in editable mode into `.venv`.

## Environment And Ports

Relevant environment variables:

```text
OHS_APP_NAME=open-health-server
OHS_ENVIRONMENT=development
OHS_API_VERSION=0.1.0
OHS_DATABASE_URL=postgresql+psycopg://ohs:ohs@localhost:5433/open_health_server
```

Docker Compose service-to-service DB URL uses internal port `5432`:

```text
postgresql+psycopg://ohs:ohs@db:5432/open_health_server
```

Local host access uses `localhost:5433`.

## What The Backend Currently Does

The FastAPI app is created in [backend/app/main.py](../../backend/app/main.py).

Registered endpoints:

```text
GET /health
GET /version
GET /docs
GET /redoc
GET /openapi.json
```

Expected endpoint responses:

```json
{
  "status": "ok"
}
```

```json
{
  "app": "open-health-server",
  "version": "0.1.0",
  "environment": "development"
}
```

The API currently has no domain endpoints. There are no `/persons`, `/metrics`, `/samples`, `/sessions`, `/logs`, or `/attributes` routes yet.

## Database Foundation

[backend/app/database.py](../../backend/app/database.py) currently defines:

- `Base`: SQLAlchemy declarative base.
- `make_engine()`: creates a SQLAlchemy engine from either an explicit URL or settings.
- `engine`: default engine from settings.
- `SessionLocal`: SQLAlchemy session factory.
- `get_db_session()`: generator for future FastAPI dependencies.
- `check_database_connection()`: executes `SELECT 1` and returns `True` on success.

[backend/app/models.py](../../backend/app/models.py) defines SQLAlchemy model classes for the Schema V1 tables:

```text
Server
User
Person
UserPersonAccess
MetricDefinition
SourceMetricMapping
Source
ImportEvent
Sample
SessionRecord
LogEntry
PersonAttribute
```

The model layer preserves database column names while avoiding unsafe Python attribute names where needed. `metric_definitions.schema` is mapped as `schema_`, and `samples.metadata` is mapped as `metadata_`.

Alembic imports `backend.app.models` in [backend/migrations/env.py](../../backend/migrations/env.py) so future autogenerate checks see the model metadata. The model metadata also includes TimescaleDB's automatically created `samples_time_idx`, because otherwise Alembic reports false drift after `samples` becomes a hypertable.

## Migration Foundation

Alembic is configured with:

```text
alembic.ini
backend/migrations/env.py
backend/migrations/script.py.mako
backend/migrations/versions/
```

Current migration head:

```text
20260611_0002
```

Migration files:

```text
backend/migrations/versions/20260611_0001_enable_timescaledb.py
backend/migrations/versions/20260611_0002_create_schema_v1_tables.py
```

The first migration runs:

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb
```

The second migration creates:

```text
servers
users
persons
user_person_access
metric_definitions
source_metric_mappings
sources
import_events
samples
sessions
logs
attributes
```

It also creates the planned core indexes and converts `samples` into a TimescaleDB hypertable partitioned by `time`.

Important implementation detail:

```sql
primary key (id, time)
```

The `samples` table uses this composite primary key because TimescaleDB requires unique constraints on hypertables to include the partition column.

The first migration downgrade currently runs:

```sql
DROP EXTENSION IF EXISTS timescaledb
```

Be careful with the downgrade once real hypertables exist; dropping TimescaleDB later may become destructive or invalid.

## Catalog State

The seed metric catalog is outside `docs/`, under `catalog/`.

Source of truth:

```text
catalog/seed-metric-catalog-v1.json
```

Human-readable companion:

```text
catalog/seed-metric-catalog-v1.md
```

Current seed metrics:

- Samples: `heart_rate`, `steps`, `blood_glucose`, `spo2`
- Attributes: `body_weight`, `height`
- Sessions: `running_session`, `sleep_session`
- Logs: `mood_log`, `pain_log`, `meal_log`, `medication_log`

The loader lives at [backend/app/commands/seed_catalog.py](../../backend/app/commands/seed_catalog.py).

Run it from the repository root:

```bash
.venv/bin/python -m backend.app.commands.seed_catalog
```

The loader validates the JSON and upserts by `metric_definitions.key`, so it can be run repeatedly without duplicating rows.

## Verification Already Performed

These commands have been run successfully:

```bash
.venv/bin/python -m pytest
```

Result:

```text
13 passed
```

```bash
.venv/bin/alembic upgrade head
```

Result:

```text
Running upgrade 20260611_0001 -> 20260611_0002, Create Schema V1 tables.
```

The Schema V1 migration was also downgraded back to `20260611_0001` and re-applied to verify that the local development schema can be dropped and recreated.

```bash
.venv/bin/alembic current
```

Result:

```text
20260611_0002 (head)
```

The migrated database was inspected and contained the expected Schema V1 tables:

```text
attributes
import_events
logs
metric_definitions
persons
samples
servers
sessions
source_metric_mappings
sources
user_person_access
users
```

The `samples` hypertable was verified through `timescaledb_information.hypertables`.

The seed catalog loader was run twice:

```bash
.venv/bin/python -m backend.app.commands.seed_catalog
```

Result:

```text
Seeded 12 metric definitions from /home/elie/Projects/open-health-server/catalog/seed-metric-catalog-v1.json.
```

The database was queried after the second run:

```text
total=12
by_kind=attribute:2,log:4,sample:4,session:2
```

```bash
.venv/bin/python - <<'PY'
from backend.app.database import check_database_connection
print(check_database_connection())
PY
```

Result:

```text
True
```

The API was started with:

```bash
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

These local requests succeeded:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/version
```

Additional checks:

```bash
docker compose config
.venv/bin/alembic check
git diff --check
```

All passed. `alembic check` reported no new upgrade operations.

Rendered local Markdown links were also checked and resolved successfully.

## Known Issues And Caveats

### Docker Port

Host port `5432` was already in use, so the Compose DB service maps:

```text
5433:5432
```

Do not change it back to `5432` unless you know the host port is free.

### TestClient Hang

`fastapi.testclient.TestClient` hung with the resolved FastAPI/Starlette stack and emitted a deprecation warning about using `httpx` with `starlette.testclient`. Tests were changed to validate route registration and route payload functions directly for now.

Do not reintroduce `TestClient` casually. If endpoint-level ASGI tests are needed later, pick a supported current approach for the installed Starlette/FastAPI versions.

### Sandbox Networking

Database connection checks from inside the restricted sandbox failed even when the Docker container was healthy. Commands that need to reach Docker or `localhost:5433` may require escalated execution.

### Generated Files

Running tests/compile/install creates ignored files:

```text
__pycache__/
.pytest_cache/
open_health_server.egg-info/
```

They are ignored and should not be committed.

### Dirty Worktree

This repo currently has many uncommitted changes from documentation and implementation work. Do not revert unrelated files. `.obsidian/` is untracked and should be left alone unless explicitly requested.

## Current Timeline Status

See [Implementation Timeline](implementation-timeline.md).

Current meaningful status:

- Phase 0: mostly complete; auth strategy remains open.
- Phase 1: complete.
- Phase 2: complete.
- Phase 3: complete.

The next unchecked work is Phase 4: core domain API.

## Recommended Next Step

Implement read-only metric catalog endpoints.

Start with:

```text
GET /metrics
GET /metrics/{key}
```

Keep this first API step read-only. The endpoints should query seeded `metric_definitions` rows and return stable response shapes before person CRUD or health-data writes are added.

## Commands For The Next Agent

Start from repo root:

```bash
.venv/bin/python -m pytest
docker compose up -d db
.venv/bin/alembic current
```

If DB is not migrated:

```bash
.venv/bin/alembic upgrade head
```

To seed or refresh the metric catalog:

```bash
.venv/bin/python -m backend.app.commands.seed_catalog
```

To inspect current Docker DB state:

```bash
docker compose ps db
docker compose logs db --tail=80
```

To stop the database when done:

```bash
docker compose stop db
```

Do not use `docker compose down -v` unless the user explicitly agrees to delete the local database volume.

## Navigation

- [Session Handoff 2026-06-11](session-handoff-2026-06-11.md)
- [Implementation Timeline](implementation-timeline.md)
- [Schema V1](schema-v1.md)
- [Metric Taxonomy and Schema](metric-taxonomy-and-schema.md)
- [Backend App](../../backend/README.md)
- [Migrations](../../backend/migrations/README.md)
- [Catalog](../../catalog/README.md)
