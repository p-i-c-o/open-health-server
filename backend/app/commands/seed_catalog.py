from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models import MetricDefinition

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CATALOG_PATH = REPO_ROOT / "catalog" / "seed-metric-catalog-v1.json"

REQUIRED_FIELDS = {
    "key",
    "kind",
    "display_name",
    "category",
    "unit",
    "value_type",
    "is_custom",
    "created_at",
    "updated_at",
}
OPTIONAL_FIELDS = {
    "description",
    "valid_min",
    "valid_max",
    "enum_values",
    "schema",
    "created_by_user_id",
}
CATALOG_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS
KIND_VALUES = {"sample", "session", "log", "attribute"}
VALUE_TYPE_VALUES = {"float", "integer", "boolean", "string", "enum", "object", "array"}


class CatalogValidationError(ValueError):
    pass


def read_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as catalog_file:
        catalog = json.load(catalog_file)

    if not isinstance(catalog, dict):
        raise CatalogValidationError("Catalog root must be an object.")

    return catalog


def parse_catalog_timestamp(value: Any, field_name: str, metric_key: str) -> datetime:
    if not isinstance(value, str):
        raise CatalogValidationError(f"{metric_key}.{field_name} must be an ISO timestamp string.")

    normalized = value.removesuffix("Z") + "+00:00" if value.endswith("Z") else value

    try:
        return datetime.fromisoformat(normalized)
    except ValueError as error:
        raise CatalogValidationError(
            f"{metric_key}.{field_name} must be an ISO timestamp string."
        ) from error


def get_metric_definitions(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    metric_definitions = catalog.get("metric_definitions")

    if not isinstance(metric_definitions, list):
        raise CatalogValidationError("Catalog must contain a metric_definitions list.")

    return metric_definitions


def validate_metric_definition(metric: dict[str, Any], seen_keys: set[str]) -> dict[str, Any]:
    if not isinstance(metric, dict):
        raise CatalogValidationError("Each metric definition must be an object.")

    unknown_fields = sorted(set(metric) - CATALOG_FIELDS)
    if unknown_fields:
        metric_key = metric.get("key", "<unknown>")
        raise CatalogValidationError(f"{metric_key} has unknown fields: {unknown_fields}.")

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in metric)
    if missing_fields:
        metric_key = metric.get("key", "<unknown>")
        raise CatalogValidationError(f"{metric_key} is missing fields: {missing_fields}.")

    key = metric["key"]
    if not isinstance(key, str) or not key:
        raise CatalogValidationError("Metric key must be a non-empty string.")

    if key in seen_keys:
        raise CatalogValidationError(f"Duplicate metric key: {key}.")
    seen_keys.add(key)

    for field_name in ("kind", "display_name", "category", "unit", "value_type"):
        if not isinstance(metric[field_name], str) or not metric[field_name]:
            raise CatalogValidationError(f"{key}.{field_name} must be a non-empty string.")

    if metric["kind"] not in KIND_VALUES:
        raise CatalogValidationError(f"{key}.kind must be one of {sorted(KIND_VALUES)}.")

    if metric["value_type"] not in VALUE_TYPE_VALUES:
        raise CatalogValidationError(
            f"{key}.value_type must be one of {sorted(VALUE_TYPE_VALUES)}."
        )

    if not isinstance(metric["is_custom"], bool):
        raise CatalogValidationError(f"{key}.is_custom must be a boolean.")

    valid_min = metric.get("valid_min")
    valid_max = metric.get("valid_max")
    if valid_min is not None and not isinstance(valid_min, int | float):
        raise CatalogValidationError(f"{key}.valid_min must be numeric or null.")
    if valid_max is not None and not isinstance(valid_max, int | float):
        raise CatalogValidationError(f"{key}.valid_max must be numeric or null.")
    if valid_min is not None and valid_max is not None and valid_min > valid_max:
        raise CatalogValidationError(f"{key}.valid_min must be less than or equal to valid_max.")

    enum_values = metric.get("enum_values")
    if metric["value_type"] == "enum" and not isinstance(enum_values, list):
        raise CatalogValidationError(f"{key}.enum_values must be a list for enum metrics.")
    if enum_values is not None and not isinstance(enum_values, list):
        raise CatalogValidationError(f"{key}.enum_values must be a list or null.")

    schema = metric.get("schema")
    if metric["value_type"] == "object" and not isinstance(schema, dict):
        raise CatalogValidationError(f"{key}.schema must be an object for object metrics.")
    if schema is not None and not isinstance(schema, dict):
        raise CatalogValidationError(f"{key}.schema must be an object or null.")

    return {
        "key": key,
        "kind": metric["kind"],
        "display_name": metric["display_name"],
        "description": metric.get("description"),
        "category": metric["category"],
        "unit": metric["unit"],
        "value_type": metric["value_type"],
        "valid_min": valid_min,
        "valid_max": valid_max,
        "enum_values": enum_values,
        "schema": schema,
        "is_custom": metric["is_custom"],
        "created_by_user_id": metric.get("created_by_user_id"),
        "created_at": parse_catalog_timestamp(metric["created_at"], "created_at", key),
        "updated_at": parse_catalog_timestamp(metric["updated_at"], "updated_at", key),
    }


def validate_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    seen_keys: set[str] = set()

    return [
        validate_metric_definition(metric, seen_keys)
        for metric in get_metric_definitions(catalog)
    ]


def build_metric_definition_upsert(rows: Sequence[dict[str, Any]]):
    table = MetricDefinition.__table__
    statement = insert(table).values(list(rows))
    update_columns = {
        column.name: getattr(statement.excluded, column.name)
        for column in table.columns
        if column.name != "key"
    }

    return statement.on_conflict_do_update(index_elements=[table.c.key], set_=update_columns)


def upsert_metric_definitions(session: Session, rows: Sequence[dict[str, Any]]) -> int:
    if not rows:
        return 0

    session.execute(build_metric_definition_upsert(rows))
    return len(rows)


def seed_catalog(session: Session, catalog_path: Path = DEFAULT_CATALOG_PATH) -> int:
    rows = validate_catalog(read_catalog(catalog_path))
    count = upsert_metric_definitions(session, rows)
    session.commit()
    return count


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load the seed metric catalog.")
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG_PATH,
        type=Path,
        help="Path to the seed metric catalog JSON file.",
    )
    return parser.parse_args(args)


def main(args: Iterable[str] | None = None) -> int:
    parsed_args = parse_args(args)

    with SessionLocal() as session:
        count = seed_catalog(session, parsed_args.catalog)

    print(f"Seeded {count} metric definitions from {parsed_args.catalog}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
