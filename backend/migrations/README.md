[Repo Home](../../README.md) / [Backend App](../README.md) / Migrations

# Migrations

This directory contains Alembic migrations for the open-health-server database.

Run migrations from the repository root:

```bash
.venv/bin/alembic upgrade head
```

The first migration enables the TimescaleDB extension. Later migrations should create the Schema V1 tables described in [docs/planning/schema-v1.md](../../docs/planning/schema-v1.md).
