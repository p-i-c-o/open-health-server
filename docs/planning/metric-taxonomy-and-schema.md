[Repo Home](../../README.md) / [Docs](../README.md) / [Planning](README.md) / Metric Taxonomy and Schema

# Metric Taxonomy and Schema

> This document explains how open-health-server should think about metric names, units, validation, source mapping, and raw imported data.

## Why this matters

open-health-server will collect data from many places: manual entries, wearable devices, phone health APIs, training platforms, home automation, and custom logic. Those systems often describe the same thing in different ways.

For example, all of these might mean the same basic metric:

- `heart_rate`
- `hr`
- `bpm`
- `HeartRate`
- Garmin's heart rate field
- HealthKit's heart rate quantity

If open-health-server stores those names exactly as they arrive, the system is easy to build at first, but harder to use later. Charts, exports, integrations, and derived metrics would all need to guess whether two fields mean the same thing.

The project should therefore define a shared metric language early. That does not mean every possible health metric must be rigidly modeled before the first version. It means known metrics should have stable names, units, types, and source mappings so the rest of the system can rely on them.

## The core idea

open-health-server should use a hybrid model:

- Store health data in the four existing shapes: samples, sessions, logs, and attributes.
- Use a metric catalog for known metrics.
- Allow custom user-defined metrics.
- Keep raw imported payloads for traceability and debugging.
- Compute derived metrics at query time instead of storing them.

This gives the project structure without making it too rigid.

## The four data shapes

The existing [metrics](metrics.md) document defines four kinds of tracked data. Those should remain the foundation.

### Samples

Samples are timestamped measurements, usually high-volume and often imported from devices.

Examples:

- Heart rate at a specific time
- Blood glucose at a specific time
- Steps counted during a time bucket
- Cycling power at a specific time

Samples are the best fit for TimescaleDB hypertables.

### Sessions

Sessions are activities with a start and end time.

Examples:

- A run
- A rowing workout
- A sleep session
- A meditation session
- A focus session

Sessions usually contain several fields. A run may have distance, duration, pace, average heart rate, split times, and notes.

### Logs

Logs are discrete entries that happened once and do not necessarily have a duration.

Examples:

- A meal
- A mood entry
- A pain entry
- A medication dose
- An illness note

Logs are often more human-entered and descriptive than samples.

### Attributes

Attributes are slow-changing facts about a person, versioned over time.

Examples:

- Weight
- Height
- VO2 max
- FTP
- Body fat percentage
- Resting heart rate baseline

Attributes should not be overwritten in place. A new measurement should create a new row so history is preserved.

## Flexible records versus a metric catalog

There are two broad ways to store metric data.

### Flexible records

A flexible approach stores metric names as strings and session/log details as JSON.

Example:

```json
{
  "metric": "heart_rate",
  "value": 72
}
```

For sessions:

```json
{
  "type": "running",
  "data": {
    "distance_km": 5.2,
    "average_heart_rate_bpm": 148
  }
}
```

This is simple and fast to implement. It also makes it easy to import new data before every field has been formally modeled.

The risk is that data quality depends on every caller doing the right thing. The system can end up with inconsistent names, unclear units, duplicate metrics, and payloads that are hard to query.

### Metric catalog

A catalog approach defines known metrics in one place.

Example:

```json
{
  "key": "heart_rate",
  "kind": "sample",
  "display_name": "Heart rate",
  "unit": "bpm",
  "value_type": "float",
  "category": "cardiovascular",
  "valid_min": 20,
  "valid_max": 240
}
```

Then stored data refers to the catalog key instead of inventing a new name each time.

This gives the API, frontend, integrations, analytics, and exports a shared vocabulary.

The risk is over-modeling. Health and lifestyle data is broad, and users will want to track things the project did not anticipate. A catalog must support custom metrics, not just built-in ones.

## Recommended direction

open-health-server should use a catalog for known metrics, while still allowing custom metrics and raw payload storage.

In practical terms:

- Known metrics use canonical keys such as `heart_rate`, `body_weight`, or `sleep_duration`.
- Each known metric has a default unit, value type, category, and allowed data shape.
- Integrations map external fields into canonical open-health-server keys.
- Raw source data is kept separately so imports can be audited or reprocessed.
- Users can create custom metrics, but must provide basic metadata such as unit and value type.

## What the catalog should define

A metric definition should answer the basic questions that every part of the system needs.

Minimum useful fields:

- `key`: stable machine name, such as `heart_rate`
- `kind`: `sample`, `session`, `log`, or `attribute`
- `display_name`: human-readable label
- `description`: short explanation of what the metric means
- `category`: broad group, such as cardiovascular, activity, sleep, nutrition
- `unit`: canonical metric unit, such as `bpm`, `kg`, `km`, `mmol/L`, or `min`
- `value_type`: float, integer, boolean, string, enum, object, or array
- `valid_min` and `valid_max`: optional sanity bounds for numeric values
- `enum_values`: allowed values when the metric is categorical
- `is_custom`: whether the metric was created by a user
- `created_at` and `updated_at`: timestamps for catalog management

Some metrics need extra structure. For example, a blood pressure reading has systolic and diastolic values. A running session has several fields. Those can be represented by field definitions linked to a session or log type.

## Source mapping

The catalog should be separate from source mappings.

The catalog says what open-health-server means by `heart_rate`.

A source mapping says how a provider expresses that same concept.

Example:

```json
{
  "source": "garmin",
  "external_name": "heartRate",
  "metric_key": "heart_rate",
  "external_unit": "bpm",
  "canonical_unit": "bpm"
}
```

Another provider may use a different field name or unit, but both can map to the same canonical metric.

This is important because source tracking is not only about imports. Users may want to compare the same metric across sources, such as weight from a smart scale versus a manual entry, or sleep duration from two different wearables.

## Raw data

Imported data should keep a copy of the raw source payload where reasonable.

Raw data is useful for:

- Debugging bad imports
- Reprocessing data after an integration mapper improves
- Showing where a value came from
- Preserving source-specific fields that open-health-server does not yet model

Raw data should not replace canonical fields. Canonical fields are what the app uses for normal queries, charts, exports, and derived metrics. Raw data is the audit trail.

## Derived metrics

Derived metrics should not be stored as primary facts.

Examples:

- BMI
- TDEE
- Training load
- ATL / CTL
- Productivity percentage
- Sleep debt

These values should be computed from stored samples, sessions, logs, and attributes when requested.

This avoids stale data. If a weight entry is corrected, BMI should change automatically the next time it is queried rather than requiring a stored BMI row to be updated.

If performance becomes a problem later, open-health-server can add caches or materialized views. Those should be treated as rebuildable query optimisations, not as the source of truth.

## Suggested database shape

The exact schema can change during implementation, but this is the intended direction.

```sql
metric_definitions {
  key text primary key
  kind text
  display_name text
  description text
  category text
  unit text
  value_type text
  valid_min double precision
  valid_max double precision
  enum_values jsonb
  is_custom boolean
  created_at timestamptz
  updated_at timestamptz
}
```

Samples can then refer to metric definitions:

```sql
samples {
  id uuid primary key
  person_id uuid
  source_id uuid
  metric_key text references metric_definitions(key)
  time timestamptz
  value double precision
  raw jsonb
  created_at timestamptz
}
```

Sessions, logs, and attributes can follow the same principle: canonical keys for known concepts, structured fields where useful, and raw data for imported source payloads.

## How this affects implementation

### API

The API should validate incoming data against the metric catalog when a known metric key is used.

For example, if `heart_rate` is defined as a sample in `bpm`, the API can reject or flag obviously invalid values and prevent it from being submitted as a log or attribute by mistake.

### Frontend

The frontend can use the catalog to build metric pickers, chart labels, unit labels, and default visualisations.

Without a catalog, the UI has to guess how to display each metric.

### Integrations

Each integration should map provider-specific names into open-health-server canonical keys.

This keeps integration code from leaking source-specific names into the rest of the application.

### Exports

Exports should include canonical metric keys, display names, units, source information, and timestamps.

Raw source payloads can optionally be included in advanced exports.

### Custom metrics

Custom metrics should be first-class, but not unstructured.

A user-created metric should still define:

- A stable key
- A display name
- A data shape
- A unit or explicit `unitless`
- A value type
- Optional bounds or enum values

This lets users extend the system without turning the database into ambiguous strings and arbitrary JSON.

## First implementation target

The first backend implementation should probably include:

- The four core data tables: `samples`, `sessions`, `logs`, and `attributes`
- A `metric_definitions` table
- A small seed catalog for common metrics
- A `sources` table
- A place to store raw imported payloads
- Basic validation for metric key, kind, unit, and value type

This is enough structure to keep the data meaningful while still allowing the project to evolve.

## Related docs

- [Metrics](metrics.md): lists the health, lifestyle, activity, and attribute data open-health-server wants to track.
- [Schema V1](schema-v1.md): translates the taxonomy into a first implementation-oriented database shape.
- [Implementation Timeline](implementation-timeline.md): describes how the schema and catalog should become a working application.
- [Backend](backend.md): sketches the first database model and explains the choice of TimescaleDB.
- [Integrations](integrations.md): lists planned input, output, and bidirectional integrations.
- [Identity Management](identity-management.md): explains why metrics belong to persons rather than directly to users.
- [Dev Notes](dev-notes.md): includes notes about source tracking, custom metrics, and logic-based data flows.
- [Planning Home](README.md): lists all planning documents.
