from copy import deepcopy

import pytest
from sqlalchemy.dialects import postgresql

from backend.app.commands.seed_catalog import (
    CatalogValidationError,
    build_metric_definition_upsert,
    read_catalog,
    validate_catalog,
)


def test_seed_catalog_file_validates() -> None:
    rows = validate_catalog(read_catalog())

    assert len(rows) == 12
    assert {row["key"] for row in rows} >= {"heart_rate", "running_session", "mood_log"}


def test_seed_catalog_rejects_duplicate_metric_keys() -> None:
    catalog = read_catalog()
    catalog["metric_definitions"].append(deepcopy(catalog["metric_definitions"][0]))

    with pytest.raises(CatalogValidationError, match="Duplicate metric key"):
        validate_catalog(catalog)


def test_seed_catalog_rejects_invalid_numeric_bounds() -> None:
    catalog = read_catalog()
    catalog["metric_definitions"][0]["valid_min"] = 300
    catalog["metric_definitions"][0]["valid_max"] = 100

    with pytest.raises(CatalogValidationError, match="valid_min"):
        validate_catalog(catalog)


def test_seed_catalog_rejects_object_metric_without_schema() -> None:
    catalog = read_catalog()
    catalog["metric_definitions"][6]["schema"] = None

    with pytest.raises(CatalogValidationError, match="schema"):
        validate_catalog(catalog)


def test_metric_definition_upsert_uses_key_conflict() -> None:
    rows = validate_catalog(read_catalog())
    statement = build_metric_definition_upsert(rows[:1])
    compiled = str(statement.compile(dialect=postgresql.dialect()))

    assert "ON CONFLICT (key) DO UPDATE" in compiled
