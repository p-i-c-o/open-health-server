from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


def uuid_pk_column() -> Mapped[UUID]:
    return mapped_column(sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def created_at_column() -> Mapped[datetime]:
    return mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )


def updated_at_column() -> Mapped[datetime]:
    return mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[UUID] = uuid_pk_column()
    name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = uuid_pk_column()
    server_id: Mapped[UUID] = mapped_column(sa.ForeignKey("servers.id"), nullable=False)
    email: Mapped[str | None] = mapped_column(sa.Text(), unique=True)
    display_name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(sa.Text())
    role: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[UUID] = uuid_pk_column()
    server_id: Mapped[UUID] = mapped_column(sa.ForeignKey("servers.id"), nullable=False)
    display_name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(sa.Date())
    sex_at_birth: Mapped[str | None] = mapped_column(sa.Text())
    notes: Mapped[str | None] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class UserPersonAccess(Base):
    __tablename__ = "user_person_access"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "person_id"),
        sa.Index("user_person_access_user_id_idx", "user_id"),
        sa.Index("user_person_access_person_id_idx", "person_id"),
    )

    id: Mapped[UUID] = uuid_pk_column()
    user_id: Mapped[UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False)
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    access_level: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    can_write: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    can_manage_access: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class MetricDefinition(Base):
    __tablename__ = "metric_definitions"
    __table_args__ = (
        sa.Index("metric_definitions_kind_idx", "kind"),
        sa.Index("metric_definitions_category_idx", "category"),
    )

    key: Mapped[str] = mapped_column(sa.Text(), primary_key=True)
    kind: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    display_name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text())
    category: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    unit: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    value_type: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    valid_min: Mapped[float | None] = mapped_column(sa.Double())
    valid_max: Mapped[float | None] = mapped_column(sa.Double())
    enum_values: Mapped[Any | None] = mapped_column(JSONB)
    schema_: Mapped[Any | None] = mapped_column("schema", JSONB)
    is_custom: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    created_by_user_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("users.id"))
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class SourceMetricMapping(Base):
    __tablename__ = "source_metric_mappings"
    __table_args__ = (sa.UniqueConstraint("source_integration", "external_name", "external_unit"),)

    id: Mapped[UUID] = uuid_pk_column()
    source_integration: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    external_name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    external_unit: Mapped[str | None] = mapped_column(sa.Text())
    metric_key: Mapped[str] = mapped_column(sa.ForeignKey("metric_definitions.key"), nullable=False)
    canonical_unit: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    transform: Mapped[Any | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class Source(Base):
    __tablename__ = "sources"
    __table_args__ = (
        sa.Index("sources_person_id_idx", "person_id"),
        sa.Index("sources_integration_idx", "integration"),
    )

    id: Mapped[UUID] = uuid_pk_column()
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    integration: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    display_name: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    external_account_id: Mapped[str | None] = mapped_column(sa.Text())
    device_name: Mapped[str | None] = mapped_column(sa.Text())
    connected_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    disconnected_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class ImportEvent(Base):
    __tablename__ = "import_events"
    __table_args__ = (
        sa.UniqueConstraint("source_id", "external_id"),
        sa.Index("import_events_source_imported_idx", "source_id", sa.desc("imported_at")),
    )

    id: Mapped[UUID] = uuid_pk_column()
    source_id: Mapped[UUID] = mapped_column(sa.ForeignKey("sources.id"), nullable=False)
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    external_id: Mapped[str | None] = mapped_column(sa.Text())
    imported_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    payload_type: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    raw_payload: Mapped[Any] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    error_message: Mapped[str | None] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = created_at_column()


class Sample(Base):
    __tablename__ = "samples"
    __table_args__ = (
        sa.Index("samples_time_idx", sa.desc("time")),
        sa.Index("samples_person_metric_time_idx", "person_id", "metric_key", sa.desc("time")),
        sa.Index("samples_source_time_idx", "source_id", sa.desc("time")),
    )

    id: Mapped[UUID] = mapped_column(
        sa.UUID(),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("sources.id"))
    import_event_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("import_events.id"))
    metric_key: Mapped[str] = mapped_column(sa.ForeignKey("metric_definitions.key"), nullable=False)
    time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), primary_key=True)
    value: Mapped[float] = mapped_column(sa.Double(), nullable=False)
    unit: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    quality: Mapped[str | None] = mapped_column(sa.Text())
    metadata_: Mapped[Any | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = created_at_column()


class SessionRecord(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        sa.Index(
            "sessions_person_type_started_idx",
            "person_id",
            "type_key",
            sa.desc("started_at"),
        ),
    )

    id: Mapped[UUID] = uuid_pk_column()
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("sources.id"))
    import_event_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("import_events.id"))
    type_key: Mapped[str] = mapped_column(sa.ForeignKey("metric_definitions.key"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    timezone: Mapped[str | None] = mapped_column(sa.Text())
    data: Mapped[Any] = mapped_column(JSONB, nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class LogEntry(Base):
    __tablename__ = "logs"
    __table_args__ = (
        sa.Index("logs_person_type_logged_idx", "person_id", "type_key", sa.desc("logged_at")),
    )

    id: Mapped[UUID] = uuid_pk_column()
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("sources.id"))
    import_event_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("import_events.id"))
    type_key: Mapped[str] = mapped_column(sa.ForeignKey("metric_definitions.key"), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    timezone: Mapped[str | None] = mapped_column(sa.Text())
    data: Mapped[Any] = mapped_column(JSONB, nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class PersonAttribute(Base):
    __tablename__ = "attributes"
    __table_args__ = (
        sa.Index(
            "attributes_person_metric_measured_idx",
            "person_id",
            "metric_key",
            sa.desc("measured_at"),
        ),
    )

    id: Mapped[UUID] = uuid_pk_column()
    person_id: Mapped[UUID] = mapped_column(sa.ForeignKey("persons.id"), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("sources.id"))
    import_event_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey("import_events.id"))
    metric_key: Mapped[str] = mapped_column(sa.ForeignKey("metric_definitions.key"), nullable=False)
    measured_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    value: Mapped[Any] = mapped_column(JSONB, nullable=False)
    unit: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = created_at_column()
