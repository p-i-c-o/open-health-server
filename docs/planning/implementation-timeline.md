[Repo Home](../../README.md) / [Docs](../README.md) / [Planning](README.md) / Implementation Timeline

# Implementation Timeline

> This document describes how open-health-server should move from planning documents into a working self-hosted application.

## Purpose

The goal of this timeline is to prepare implementation without rushing into code before the core shape is clear. It turns the current planning work into phases that can be built, reviewed, and revised in order.

This is not a calendar schedule. It is a dependency-aware build order. A phase is ready when its exit criteria are met, not when a fixed number of days has passed.

## Current Inputs

The timeline assumes these planning artifacts already exist:

- [x] [Metrics](metrics.md): broad list of health, lifestyle, activity, log, and attribute data.
- [x] [Metric Taxonomy and Schema](metric-taxonomy-and-schema.md): design rationale for canonical metric keys, units, source mappings, raw payloads, and derived metrics.
- [x] [Schema V1](schema-v1.md): first implementation-oriented database shape.
- [x] [Identity Management](identity-management.md): separation between users and persons.
- [x] [Integrations](integrations.md): first list of planned inputs, outputs, and bidirectional integrations.
- [x] [Catalog](../../catalog/README.md): seed metric catalog files outside the docs tree.

## Guiding Approach

- Build the backend foundation first.
- Keep the first implementation narrow enough to finish.
- Make data model decisions explicit before frontend decisions depend on them.
- Prefer migrations and seed files over hand-created database state.
- Make the API expose the catalog instead of hardcoding metric knowledge in the frontend.
- Keep integrations behind clear source/import boundaries.
- Treat derived metrics as query behavior, not stored primary data.

## Phase 0: Planning Closure

Phase 0 finishes the design work needed before a backend scaffold is created.

Status: Mostly complete. Auth details remain deliberately deferred.

### Deliverables

- [x] Confirm [Schema V1](schema-v1.md) as the initial database target.
- [x] Confirm [seed-metric-catalog-v1.json](../../catalog/seed-metric-catalog-v1.json) as the initial seed catalog.
- [x] Decide the backend stack.
- [x] Decide migration tooling.
- [ ] Decide initial auth strategy.
- [x] Decide local development/deployment shape.

### Recommended Decisions

- [x] Backend: FastAPI unless there is a strong preference for another stack.
- [x] Database: PostgreSQL with TimescaleDB enabled from the start.
- [x] Migrations: Alembic if using FastAPI/Python.
- [x] API style: REST first, OpenAPI generated from route/schema definitions.
- [ ] Auth: local email/password first, with password hashes and session/JWT strategy decided during implementation.
- [x] Local dev: Docker Compose for database and app services.
- [x] Frontend: defer until the API can expose persons, catalog, and basic data reads/writes.

### Exit Criteria

- [x] The project has a chosen backend stack.
- [x] The first migration target is understood.
- [x] Open questions that block scaffolding are either answered or deliberately deferred.

## Phase 1: Backend Skeleton

Phase 1 creates the minimal backend project with no health-domain complexity beyond being able to run.

Status: Complete. The app skeleton, Docker Compose database, database connection helper, Alembic baseline, and system tests are in place.

### Deliverables

- [x] Backend app directory.
- [x] Dependency manifest.
- [x] Development server command.
- [x] Basic config loading.
- [x] Healthcheck endpoint.
- [x] Database connection setup.
- [x] Docker Compose file with TimescaleDB.
- [x] Empty migration baseline.

### First Useful Endpoints

```text
GET /health
GET /version
```

Endpoint progress:

- [x] `GET /health`
- [x] `GET /version`

### Exit Criteria

- [x] A developer can start the database and backend locally.
- [x] The backend can connect to the database.
- [x] A healthcheck route exists and has passing tests.
- [x] Migration tooling can run against an empty database.

## Phase 2: Schema Migration

Phase 2 turns [Schema V1](schema-v1.md) into real database migrations.

Status: Complete. Schema V1 is implemented by migration `20260611_0002_create_schema_v1_tables.py`, with `samples` configured as a TimescaleDB hypertable.

### Deliverables

- [x] Migration for identity/core tables: `servers`, `users`, `persons`, `user_person_access`.
- [x] Migration for catalog/source tables: `metric_definitions`, `source_metric_mappings`, `sources`, `import_events`.
- [x] Migration for health data tables: `samples`, `sessions`, `logs`, `attributes`.
- [x] TimescaleDB setup for `samples`.
- [x] Indexes described in [Schema V1](schema-v1.md), adjusted for the actual database syntax.
- [x] SQLAlchemy model metadata for the Schema V1 tables.

### Implementation Notes

- [x] Use plain text plus application-level validation for enum-like fields at first unless database enums clearly reduce complexity.
- [x] Keep raw import payloads in `import_events`, not repeated across high-volume sample rows.
- [x] Keep `samples` narrow and query-friendly.
- [x] Allow `sessions`, `logs`, and `attributes` to use JSON where the shape varies.
- [x] Use a composite primary key on `samples(id, time)` so the table can be converted into a TimescaleDB hypertable.
- [x] Include the Timescale-created `samples_time_idx` in model metadata so Alembic autogenerate does not report false drift.

### Exit Criteria

- [x] A fresh database can migrate from empty to Schema V1.
- [x] The schema can be dropped and recreated in development.
- [x] Foreign keys and core indexes exist.
- [x] `samples` is configured as a TimescaleDB hypertable or has a documented reason to defer that step.
- [x] Alembic autogenerate check reports no pending model/database drift.

## Phase 3: Seed Catalog Loading

Phase 3 makes the seed catalog usable by the backend.

Status: Complete. The seed catalog loader validates `seed-metric-catalog-v1.json` and upserts the 12 seed metrics into `metric_definitions`.

### Deliverables

- [x] Loader for [seed-metric-catalog-v1.json](../../catalog/seed-metric-catalog-v1.json).
- [x] Idempotent insert/update behavior for `metric_definitions`.
- [x] Basic validation during load.
- [x] A documented command for loading or refreshing seed metrics.

### Basic Validation

- [x] Required fields exist.
- [x] Metric keys are unique.
- [x] `kind` is one of `sample`, `session`, `log`, or `attribute`.
- [x] `value_type` is one of the accepted value types.
- [x] Numeric bounds are coherent when both are present.
- [x] Object metrics have a schema when needed.

### Exit Criteria

- [x] A fresh database can be migrated and seeded.
- [x] Re-running the seed command does not duplicate metrics.
- [x] The backend can query the seeded metric definitions.

## Phase 4: Core Domain API

Phase 4 exposes the smallest API surface needed to interact with persons and metric definitions.

### Deliverables

- [ ] API models for persons.
- [ ] API models for metric definitions.
- [ ] Read endpoints for the seed catalog.
- [ ] Basic create/read/update endpoints for persons.
- [x] OpenAPI output available from the backend framework.

### First Useful Endpoints

```text
GET /metrics
GET /metrics/{key}
GET /persons
POST /persons
GET /persons/{person_id}
PATCH /persons/{person_id}
```

Endpoint progress:

- [ ] `GET /metrics`
- [ ] `GET /metrics/{key}`
- [ ] `GET /persons`
- [ ] `POST /persons`
- [ ] `GET /persons/{person_id}`
- [ ] `PATCH /persons/{person_id}`

### Exit Criteria

- [ ] A client can list canonical metrics.
- [ ] A client can create and retrieve a person.
- [ ] API responses match the database model closely enough that frontend work can start without guessing field names.

## Phase 5: Manual Data Writes

Phase 5 makes the core health tables usable without integrations.

### Deliverables

- [ ] Sample write/read endpoints.
- [ ] Session write/read endpoints.
- [ ] Log write/read endpoints.
- [ ] Attribute write/read endpoints.
- [ ] Application-level validation against `metric_definitions`.
- [ ] Clear handling for manual source/null source convention.

### First Useful Endpoints

```text
POST /persons/{person_id}/samples
GET /persons/{person_id}/samples
POST /persons/{person_id}/sessions
GET /persons/{person_id}/sessions
POST /persons/{person_id}/logs
GET /persons/{person_id}/logs
POST /persons/{person_id}/attributes
GET /persons/{person_id}/attributes
```

Endpoint progress:

- [ ] `POST /persons/{person_id}/samples`
- [ ] `GET /persons/{person_id}/samples`
- [ ] `POST /persons/{person_id}/sessions`
- [ ] `GET /persons/{person_id}/sessions`
- [ ] `POST /persons/{person_id}/logs`
- [ ] `GET /persons/{person_id}/logs`
- [ ] `POST /persons/{person_id}/attributes`
- [ ] `GET /persons/{person_id}/attributes`

### Validation Rules

- [ ] A sample can only use a metric where `kind = sample`.
- [ ] A session can only use a metric where `kind = session`.
- [ ] A log can only use a metric where `kind = log`.
- [ ] An attribute can only use a metric where `kind = attribute`.
- [ ] Units must match the catalog or be converted before storage.
- [ ] Numeric bounds and enum values must be checked when defined.

### Exit Criteria

- [ ] Manual entries can populate all four health data shapes.
- [ ] Invalid metric kind usage is rejected.
- [ ] The API can return data by person, metric/type, and time range.

## Phase 6: Minimal Frontend

Phase 6 starts the frontend only after the backend can expose enough structure to avoid hardcoded guesses.

### Deliverables

- [ ] App shell.
- [ ] Person selector.
- [ ] Metric catalog viewer.
- [ ] Basic manual entry forms for at least one sample, one attribute, one session, and one log.
- [ ] Simple timeline/list views for entered data.

### First Frontend Workflows

- [ ] Select a person.
- [ ] View available metrics.
- [ ] Enter body weight.
- [ ] Enter mood log.
- [ ] Enter a running session.
- [ ] View recent entries.

### Exit Criteria

- [ ] A user can create a person and manually enter useful data from the UI.
- [ ] The UI gets labels, units, and field expectations from the API where possible.
- [ ] No integration is required to prove the core app loop.

## Phase 7: Import Pipeline

Phase 7 introduces the generic import path before provider-specific integrations become complex.

### Deliverables

- [ ] Source creation/listing endpoints.
- [ ] Import event creation.
- [ ] Raw payload storage.
- [ ] Mapping from source payload to canonical rows.
- [ ] Initial manual or file-based import path.

### First Useful Flow

```text
source payload -> import_events -> source_metric_mappings -> samples/sessions/logs/attributes
```

### Exit Criteria

- [ ] The backend can store raw import payloads.
- [ ] Imported canonical rows keep `source_id` and `import_event_id`.
- [ ] Failed or ignored imports are visible in `import_events`.

## Phase 8: First Real Integration

Phase 8 adds one real integration to prove the source mapping model.

### Recommended First Integration

Start with an import/export format before OAuth-heavy provider integrations.

Good candidates:

- [ ] CSV import
- [ ] JSON import
- [ ] Health Connect export file import
- [ ] Apple Health export import

Avoid starting with Garmin, Fitbit, Oura, or Strava unless API access is already solved.

### Deliverables

- [ ] One provider/import format adapter.
- [ ] Source mapping entries for imported fields.
- [ ] Import documentation.
- [ ] Error reporting for unsupported fields.

### Exit Criteria

- [ ] A user can import real external data.
- [ ] Imported rows use canonical metric keys.
- [ ] Raw payloads remain available for debugging or reprocessing.

## Phase 9: Derived Metrics and Analytics

Phase 9 adds computed views after enough base data exists.

### First Derived Metrics

- [ ] BMI from height and body weight.
- [ ] Sleep duration summaries from sleep sessions.
- [ ] Running volume by week.
- [ ] Resting or average heart rate summaries.

### Deliverables

- [ ] Query functions or service layer for derived metrics.
- [ ] API endpoints for computed summaries.
- [ ] Clear distinction between stored facts and computed results.

### Exit Criteria

- [ ] Derived values are computed from stored data.
- [ ] Corrections to source data affect computed results without manually updating derived rows.
- [ ] Expensive queries have a path toward caching or materialized views later.

## Phase 10: Hardening and Self-Hosting

Phase 10 prepares the app for real self-hosted use.

### Deliverables

- [ ] Production Docker Compose example.
- [ ] Environment variable documentation.
- [ ] Backup and restore notes.
- [ ] Authentication hardening.
- [ ] Basic audit/error logging.
- [ ] Upgrade/migration notes.

### Exit Criteria

- [ ] A user can deploy the app locally or on a small server.
- [ ] Data can be backed up and restored.
- [ ] App upgrades have a migration path.

## Re-Iteration Checkpoints

Revisit the plan after each major phase.

### After Phase 2

Check whether Schema V1 still feels right once expressed as real migrations.

Questions:

- [ ] Are any tables doing too much?
- [ ] Are JSON fields hiding data that should be queryable?
- [ ] Are indexes aligned with expected queries?
- [ ] Is TimescaleDB setup straightforward?

### After Phase 3

Check whether the seed catalog is expressive enough.

Questions:

- [ ] Are sessions/logs too loosely modeled?
- [ ] Are units and value types consistent?
- [ ] Do custom metrics need a stronger design?
- [ ] Should source mappings be seeded now or later?

### After Phase 5

Check whether the manual API is ergonomic.

Questions:

- [ ] Are write payloads simple enough?
- [ ] Does validation produce useful errors?
- [ ] Are query endpoints shaped for frontend use?
- [ ] Is the person/user separation clear in practice?

### After Phase 8

Check whether imports stress the model.

Questions:

- [ ] Are raw payloads sufficient for debugging?
- [ ] Are source mappings expressive enough?
- [ ] Are duplicate imports handled safely?
- [ ] Are external units converted consistently?

## Deferred Until Later

These are important but should not block the first working loop:

- [ ] Multiple real OAuth integrations.
- [ ] Advanced permissions beyond owner/manager/viewer.
- [ ] Complex dashboards.
- [ ] Mobile app.
- [ ] Public plugin system.
- [ ] Complex derived-metric DSL.
- [ ] Long-term compression and retention policy tuning.

## Related Docs

- [Current Implementation State](current-implementation-state.md)
- [Schema V1](schema-v1.md)
- [Metric Taxonomy and Schema](metric-taxonomy-and-schema.md)
- [Backend](backend.md)
- [Identity Management](identity-management.md)
- [Integrations](integrations.md)
- [Catalog](../../catalog/README.md)
