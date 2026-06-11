[Repo Home](../../README.md) / [Docs](../README.md) / [Planning](README.md) / Integrations

# Integrations

> This document outlines what integrations open-health-server has, and what they can do.

See [Metric Taxonomy and Schema](metric-taxonomy-and-schema.md) for how integration-specific fields should map into canonical open-health-server metrics and units.

## Inputs
- Garmin Connect
- Health Connect (Android ecosystem)
- Health Kit (Apple ecosystem)
- Fitbit
- Oura
- Whoop
- MyFitnessPal [^1]

## Outputs
- Strava [^2]
- CSV / JSON Export

## Bi-directional
- n8n
- Home Assistant
- open-health-server API

[^1]: MyFitnessPal is known for having shaky API support, might not integrate? Depends on what they do ...
[^2]: I'm leaving Strava as an output only due to it's social-media oriented behaviour.

## Related docs

- [Metric Taxonomy and Schema](metric-taxonomy-and-schema.md)
- [Metrics](metrics.md)
- [Backend](backend.md)
