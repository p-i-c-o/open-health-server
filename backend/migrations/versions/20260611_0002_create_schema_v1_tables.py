"""Create Schema V1 tables.

Revision ID: 20260611_0002
Revises: 20260611_0001
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260611_0002"
down_revision = "20260611_0001"
branch_labels = None
depends_on = None


def uuid_column(name: str = "id") -> sa.Column:
    return sa.Column(name, postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False)


def created_at_column() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False)


def updated_at_column() -> sa.Column:
    return sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "servers",
        uuid_column(),
        sa.Column("name", sa.Text(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        uuid_column(),
        sa.Column("server_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("role", sa.Text(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["server_id"], ["servers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "persons",
        uuid_column(),
        sa.Column("server_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("sex_at_birth", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["server_id"], ["servers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_person_access",
        uuid_column(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("access_level", sa.Text(), nullable=False),
        sa.Column("can_write", sa.Boolean(), nullable=False),
        sa.Column("can_manage_access", sa.Boolean(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "person_id"),
    )

    op.create_table(
        "metric_definitions",
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("value_type", sa.Text(), nullable=False),
        sa.Column("valid_min", sa.Double(), nullable=True),
        sa.Column("valid_max", sa.Double(), nullable=True),
        sa.Column("enum_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("schema", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "source_metric_mappings",
        uuid_column(),
        sa.Column("source_integration", sa.Text(), nullable=False),
        sa.Column("external_name", sa.Text(), nullable=False),
        sa.Column("external_unit", sa.Text(), nullable=True),
        sa.Column("metric_key", sa.Text(), nullable=False),
        sa.Column("canonical_unit", sa.Text(), nullable=False),
        sa.Column("transform", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["metric_key"], ["metric_definitions.key"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_integration", "external_name", "external_unit"),
    )

    op.create_table(
        "sources",
        uuid_column(),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("integration", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("external_account_id", sa.Text(), nullable=True),
        sa.Column("device_name", sa.Text(), nullable=True),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "import_events",
        uuid_column(),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload_type", sa.Text(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        created_at_column(),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id"),
    )

    op.create_table(
        "samples",
        uuid_column(),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("import_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metric_key", sa.Text(), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Double(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("quality", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        created_at_column(),
        sa.ForeignKeyConstraint(["import_event_id"], ["import_events.id"]),
        sa.ForeignKeyConstraint(["metric_key"], ["metric_definitions.key"]),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id", "time"),
    )
    op.execute("SELECT create_hypertable('samples', 'time', if_not_exists => TRUE)")

    op.create_table(
        "sessions",
        uuid_column(),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("import_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type_key", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.Text(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["import_event_id"], ["import_events.id"]),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["type_key"], ["metric_definitions.key"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "logs",
        uuid_column(),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("import_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type_key", sa.Text(), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["import_event_id"], ["import_events.id"]),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["type_key"], ["metric_definitions.key"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "attributes",
        uuid_column(),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("import_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metric_key", sa.Text(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        created_at_column(),
        sa.ForeignKeyConstraint(["import_event_id"], ["import_events.id"]),
        sa.ForeignKeyConstraint(["metric_key"], ["metric_definitions.key"]),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("user_person_access_user_id_idx", "user_person_access", ["user_id"])
    op.create_index("user_person_access_person_id_idx", "user_person_access", ["person_id"])
    op.create_index("sources_person_id_idx", "sources", ["person_id"])
    op.create_index("sources_integration_idx", "sources", ["integration"])
    op.create_index("metric_definitions_kind_idx", "metric_definitions", ["kind"])
    op.create_index("metric_definitions_category_idx", "metric_definitions", ["category"])
    op.create_index("samples_person_metric_time_idx", "samples", ["person_id", "metric_key", sa.text("time DESC")])
    op.create_index("samples_source_time_idx", "samples", ["source_id", sa.text("time DESC")])
    op.create_index("sessions_person_type_started_idx", "sessions", ["person_id", "type_key", sa.text("started_at DESC")])
    op.create_index("logs_person_type_logged_idx", "logs", ["person_id", "type_key", sa.text("logged_at DESC")])
    op.create_index("attributes_person_metric_measured_idx", "attributes", ["person_id", "metric_key", sa.text("measured_at DESC")])
    op.create_index("import_events_source_imported_idx", "import_events", ["source_id", sa.text("imported_at DESC")])


def downgrade() -> None:
    op.drop_table("attributes")
    op.drop_table("logs")
    op.drop_table("sessions")
    op.drop_table("samples")
    op.drop_table("import_events")
    op.drop_table("sources")
    op.drop_table("source_metric_mappings")
    op.drop_table("metric_definitions")
    op.drop_table("user_person_access")
    op.drop_table("persons")
    op.drop_table("users")
    op.drop_table("servers")
