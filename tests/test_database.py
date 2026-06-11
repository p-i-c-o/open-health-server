from sqlalchemy import create_engine

import backend.app.models  # noqa: F401
from backend.app.database import Base, check_database_connection, make_engine


def test_metadata_has_schema_v1_tables() -> None:
    expected_tables = {
        "servers",
        "users",
        "persons",
        "user_person_access",
        "metric_definitions",
        "source_metric_mappings",
        "sources",
        "import_events",
        "samples",
        "sessions",
        "logs",
        "attributes",
    }

    assert set(Base.metadata.tables) == expected_tables


def test_sample_model_uses_timescale_compatible_primary_key() -> None:
    sample_table = Base.metadata.tables["samples"]

    assert [column.name for column in sample_table.primary_key.columns] == ["id", "time"]


def test_reserved_database_column_names_have_safe_model_attributes() -> None:
    metric_definitions = Base.metadata.tables["metric_definitions"]
    samples = Base.metadata.tables["samples"]

    assert "schema" in metric_definitions.columns
    assert "metadata" in samples.columns


def test_make_engine_uses_explicit_database_url() -> None:
    engine = make_engine("sqlite+pysqlite:///:memory:")

    assert str(engine.url) == "sqlite+pysqlite:///:memory:"


def test_check_database_connection() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    assert check_database_connection(engine) is True
