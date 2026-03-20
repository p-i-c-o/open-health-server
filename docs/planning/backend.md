[Go back to planning home](README.md)

# Backend

> This document outlines how the backend of open-health-server works.


## Data Storage Design
```mermaid
erDiagram
  servers ||--o{ people : has
  people ||--o{ samples : owns
  people ||--o{ sessions : owns
  people ||--o{ logs : owns
  people ||--o{ attributes : owns
  sources ||--o{ samples : tags

  servers {
    uuid id PK
    string name
    timestamp created_at
  }
  people {
    uuid id PK
    uuid server_id FK
    string display_name
    timestamp created_at
  }
  sources {
    uuid id PK
    uuid person_id FK
    string integration
    string device_name
    timestamp connected_at
  }
  samples {
    uuid id PK
    uuid person_id FK
    uuid source_id FK
    timestamp time
    string metric
    float value
  }
  sessions {
    uuid id PK
    uuid person_id FK
    uuid source_id FK
    string type
    timestamp started_at
    timestamp ended_at
    jsonb data
  }
  logs {
    uuid id PK
    uuid person_id FK
    string type
    timestamp logged_at
    jsonb data
  }
  attributes {
    uuid id PK
    uuid person_id FK
    string key
    float value
    timestamp measured_at
    uuid source_id FK
  }
```

### Justification
open-health-server uses TimescaleDB as its database engine. TimescaleDB is a PostgreSQL extension purpose-built for time-series data, and since the majority of OHS data is time-stamped health metrics, it is the natural fit. It provides automatic partitioning of data by time, query optimisation over large date ranges, and built-in compression for older data, all while remaining fully compatible with standard PostgreSQL tooling, drivers, and syntax. Starting with TimescaleDB from day one avoids a painful migration later as data volumes grow, and ensures the system is architected to scale to billions of rows without fundamental changes to the database layer.