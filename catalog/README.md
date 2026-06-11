[Repo Home](../README.md) / Catalog

# Catalog

This directory contains seed catalog data that can later be loaded by migrations, backend startup code, or admin tooling.

## Files

- [seed-metric-catalog-v1.json](seed-metric-catalog-v1.json): machine-readable source of truth for the initial `metric_definitions` seed data.
- [seed-metric-catalog-v1.md](seed-metric-catalog-v1.md): human-readable view of the same seed metrics, split into separate formatted code blocks for review.

## Current Seed Groups

- Samples: `heart_rate`, `steps`, `blood_glucose`, `spo2`
- Attributes: `body_weight`, `height`
- Sessions: `running_session`, `sleep_session`
- Logs: `mood_log`, `pain_log`, `meal_log`, `medication_log`

## Loading

From the repository root, load or refresh the seed catalog with:

```bash
.venv/bin/python -m backend.app.commands.seed_catalog
```

The loader validates the JSON and upserts into `metric_definitions`, so it can be run repeatedly without duplicating rows.
