[Repo Home](../README.md) / [Catalog](README.md) / Seed Metric Catalog V1

# Seed Metric Catalog V1

Source file: [seed-metric-catalog-v1.json](seed-metric-catalog-v1.json)

This file is a human-readable companion to the JSON seed catalog. The JSON file is the source of truth; this Markdown file splits each metric definition into its own formatted code block for easier review.

## Samples

### `heart_rate`

```json
{
  "key": "heart_rate",
  "kind": "sample",
  "display_name": "Heart rate",
  "description": "Instantaneous heart beats per minute.",
  "category": "cardiovascular",
  "unit": "bpm",
  "value_type": "float",
  "valid_min": 20,
  "valid_max": 240,
  "enum_values": null,
  "schema": null,
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `steps`

```json
{
  "key": "steps",
  "kind": "sample",
  "display_name": "Steps",
  "description": "Step count for a timestamp or time bucket.",
  "category": "activity",
  "unit": "count",
  "value_type": "integer",
  "valid_min": 0,
  "valid_max": 250000,
  "enum_values": null,
  "schema": null,
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `blood_glucose`

```json
{
  "key": "blood_glucose",
  "kind": "sample",
  "display_name": "Blood glucose",
  "description": "Blood glucose concentration.",
  "category": "metabolic",
  "unit": "mmol/L",
  "value_type": "float",
  "valid_min": 1,
  "valid_max": 40,
  "enum_values": null,
  "schema": null,
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `spo2`

```json
{
  "key": "spo2",
  "kind": "sample",
  "display_name": "SpO2",
  "description": "Peripheral blood oxygen saturation percentage.",
  "category": "respiratory",
  "unit": "%",
  "value_type": "float",
  "valid_min": 50,
  "valid_max": 100,
  "enum_values": null,
  "schema": null,
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

## Attributes

### `body_weight`

```json
{
  "key": "body_weight",
  "kind": "attribute",
  "display_name": "Body weight",
  "description": "Measured body weight.",
  "category": "body",
  "unit": "kg",
  "value_type": "float",
  "valid_min": 1,
  "valid_max": 500,
  "enum_values": null,
  "schema": null,
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `height`

```json
{
  "key": "height",
  "kind": "attribute",
  "display_name": "Height",
  "description": "Measured body height.",
  "category": "body",
  "unit": "cm",
  "value_type": "float",
  "valid_min": 30,
  "valid_max": 260,
  "enum_values": null,
  "schema": null,
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

## Sessions

### `running_session`

```json
{
  "key": "running_session",
  "kind": "session",
  "display_name": "Running session",
  "description": "A running workout with distance, duration, heart rate, pace, and optional route metrics.",
  "category": "activity",
  "unit": "unitless",
  "value_type": "object",
  "valid_min": null,
  "valid_max": null,
  "enum_values": null,
  "schema": {
    "type": "object",
    "properties": {
      "distance_km": {
        "type": "number",
        "minimum": 0
      },
      "duration_min": {
        "type": "number",
        "minimum": 0
      },
      "pace_min_per_km": {
        "type": "number",
        "minimum": 0
      },
      "average_heart_rate_bpm": {
        "type": "number",
        "minimum": 20,
        "maximum": 240
      },
      "max_heart_rate_bpm": {
        "type": "number",
        "minimum": 20,
        "maximum": 240
      },
      "active_calories_kcal": {
        "type": "number",
        "minimum": 0
      },
      "cadence_steps_per_min": {
        "type": "number",
        "minimum": 0
      },
      "elevation_gain_m": {
        "type": "number"
      }
    },
    "required": [
      "distance_km",
      "duration_min"
    ],
    "additionalProperties": true
  },
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `sleep_session`

```json
{
  "key": "sleep_session",
  "kind": "session",
  "display_name": "Sleep session",
  "description": "A sleep period with duration and optional stage breakdown.",
  "category": "sleep",
  "unit": "unitless",
  "value_type": "object",
  "valid_min": null,
  "valid_max": null,
  "enum_values": null,
  "schema": {
    "type": "object",
    "properties": {
      "total_duration_min": {
        "type": "number",
        "minimum": 0,
        "maximum": 1440
      },
      "rem_duration_min": {
        "type": "number",
        "minimum": 0,
        "maximum": 1440
      },
      "deep_duration_min": {
        "type": "number",
        "minimum": 0,
        "maximum": 1440
      },
      "light_duration_min": {
        "type": "number",
        "minimum": 0,
        "maximum": 1440
      },
      "awake_duration_min": {
        "type": "number",
        "minimum": 0,
        "maximum": 1440
      },
      "sleep_onset_latency_min": {
        "type": "number",
        "minimum": 0,
        "maximum": 1440
      },
      "wake_events": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [
      "total_duration_min"
    ],
    "additionalProperties": true
  },
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

## Logs

### `mood_log`

```json
{
  "key": "mood_log",
  "kind": "log",
  "display_name": "Mood log",
  "description": "Manual or imported mood and mental state check-in.",
  "category": "mental_state",
  "unit": "unitless",
  "value_type": "object",
  "valid_min": null,
  "valid_max": null,
  "enum_values": null,
  "schema": {
    "type": "object",
    "properties": {
      "mood": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      },
      "stress": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      },
      "anxiety": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      },
      "energy": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      },
      "social_battery": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      },
      "journal": {
        "type": "string"
      }
    },
    "required": [
      "mood"
    ],
    "additionalProperties": true
  },
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `pain_log`

```json
{
  "key": "pain_log",
  "kind": "log",
  "display_name": "Pain log",
  "description": "Pain entry with location, intensity, and optional pain type.",
  "category": "physical_state",
  "unit": "unitless",
  "value_type": "object",
  "valid_min": null,
  "valid_max": null,
  "enum_values": null,
  "schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string"
      },
      "intensity": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      },
      "type": {
        "type": "string",
        "enum": [
          "sharp",
          "dull",
          "aching",
          "burning",
          "other"
        ]
      },
      "notes": {
        "type": "string"
      }
    },
    "required": [
      "location",
      "intensity"
    ],
    "additionalProperties": true
  },
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `meal_log`

```json
{
  "key": "meal_log",
  "kind": "log",
  "display_name": "Meal log",
  "description": "Nutrition entry for a meal or snack.",
  "category": "nutrition",
  "unit": "unitless",
  "value_type": "object",
  "valid_min": null,
  "valid_max": null,
  "enum_values": null,
  "schema": {
    "type": "object",
    "properties": {
      "description": {
        "type": "string"
      },
      "calories_kcal": {
        "type": "number",
        "minimum": 0
      },
      "protein_g": {
        "type": "number",
        "minimum": 0
      },
      "carbohydrates_g": {
        "type": "number",
        "minimum": 0
      },
      "fat_g": {
        "type": "number",
        "minimum": 0
      },
      "fiber_g": {
        "type": "number",
        "minimum": 0
      },
      "sodium_mg": {
        "type": "number",
        "minimum": 0
      }
    },
    "required": [
      "description"
    ],
    "additionalProperties": true
  },
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```

### `medication_log`

```json
{
  "key": "medication_log",
  "kind": "log",
  "display_name": "Medication log",
  "description": "Medication dose entry.",
  "category": "supplements_medications",
  "unit": "unitless",
  "value_type": "object",
  "valid_min": null,
  "valid_max": null,
  "enum_values": null,
  "schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      },
      "dose_amount": {
        "type": "number",
        "minimum": 0
      },
      "dose_unit": {
        "type": "string"
      },
      "route": {
        "type": "string"
      },
      "taken": {
        "type": "boolean"
      },
      "notes": {
        "type": "string"
      }
    },
    "required": [
      "name",
      "dose_amount",
      "dose_unit"
    ],
    "additionalProperties": true
  },
  "is_custom": false,
  "created_by_user_id": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z"
}
```
