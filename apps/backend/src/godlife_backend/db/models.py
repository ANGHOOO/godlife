from __future__ import annotations

import uuid
from datetime import date, datetime, time

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import (
    NotificationStatus,
    OutboxStatus,
    PlanStatus,
    ReadingLogStatus,
    SetStatus,
    UserStatus,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    kakao_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(80), nullable=False, default="Asia/Seoul"
    )
    status: Mapped[UserStatus] = mapped_column(
        SqlEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    profile: Mapped[UserProfile] = relationship(back_populates="user", uselist=False)
    exercise_plans: Mapped[list[ExercisePlan]] = relationship(back_populates="user")
    reading_plans: Mapped[list[ReadingPlan]] = relationship(back_populates="user")
    reading_logs: Mapped[list[ReadingLog]] = relationship(back_populates="user")
    notifications: Mapped[list[Notification]] = relationship(back_populates="user")

    __table_args__ = (Index("ix_users_kakao_user_id", "kakao_user_id"),)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    age: Mapped[int | None] = mapped_column(Integer)
    height_cm: Mapped[float | None] = mapped_column(sa.Float())
    weight_kg: Mapped[float | None] = mapped_column(sa.Float())
    goal: Mapped[str | None] = mapped_column(String(80))
    experience_level: Mapped[str | None] = mapped_column(String(80))
    max_daily_minutes: Mapped[int | None] = mapped_column(Integer)
    available_equipment: Mapped[str | None] = mapped_column(Text)
    injury_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="profile")


class ExercisePlan(Base):
    __tablename__ = "exercise_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[PlanStatus] = mapped_column(
        SqlEnum(PlanStatus), nullable=False, default=PlanStatus.DRAFT
    )
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="exercise_plans")
    sessions: Mapped[list[ExerciseSession]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_exercise_plans_target_date_status", "target_date", "status"),
        Index("ix_exercise_plans_user_id_target_date", "user_id", "target_date"),
    )


class ExerciseSession(Base):
    __tablename__ = "exercise_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_no: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(120), nullable=False)
    body_part: Mapped[str | None] = mapped_column(String(120))
    target_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    target_reps: Mapped[int | None] = mapped_column(Integer)
    target_weight_kg: Mapped[float | None] = mapped_column(sa.Float())
    target_rest_sec: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    plan: Mapped[ExercisePlan] = relationship(back_populates="sessions")
    set_states: Mapped[list[ExerciseSetState]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ExerciseSetState(Base):
    __tablename__ = "exercise_set_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    set_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SetStatus] = mapped_column(
        SqlEnum(SetStatus), nullable=False, default=SetStatus.PENDING
    )
    performed_reps: Mapped[int | None] = mapped_column(Integer)
    performed_weight_kg: Mapped[float | None] = mapped_column(sa.Float())
    actual_rest_sec: Mapped[int | None] = mapped_column(Integer)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    skipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    session: Mapped[ExerciseSession] = relationship(back_populates="set_states")

    __table_args__ = (
        UniqueConstraint("session_id", "set_no", name="uq_set_states_session_set_no"),
        Index("ix_exercise_set_states_session_id", "session_id"),
        Index("ix_exercise_set_states_status", "status"),
    )


class ReadingPlan(Base):
    __tablename__ = "reading_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    remind_time: Mapped[time] = mapped_column(sa.Time(), nullable=False)
    goal_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="reading_plans")


class ReadingLog(Base):
    __tablename__ = "reading_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    reading_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reading_plans.id", ondelete="SET NULL"),
        nullable=True,
    )
    book_title: Mapped[str | None] = mapped_column(String(255))
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pages_read: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[ReadingLogStatus] = mapped_column(
        SqlEnum(ReadingLogStatus), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="reading_logs")

    __table_args__ = (
        Index("ix_reading_logs_user_created_at", "user_id", "created_at"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(String(80), nullable=False)
    related_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    status: Mapped[NotificationStatus] = mapped_column(
        SqlEnum(NotificationStatus),
        nullable=False,
        default=NotificationStatus.SCHEDULED,
    )
    schedule_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    idempotency_key: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    provider_msg_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    reason_code: Mapped[str | None] = mapped_column(String(128))
    provider_response_code: Mapped[str | None] = mapped_column(String(64))
    failure_reason: Mapped[str | None] = mapped_column(Text)
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    memo: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[str | None] = mapped_column(String(120))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="notifications")

    __table_args__ = (
        Index(
            "ix_notifications_user_status_schedule", "user_id", "status", "schedule_at"
        ),
    )


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT")
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    event_id: Mapped[str | None] = mapped_column(String(255))
    schema_version: Mapped[str] = mapped_column(
        String(16), nullable=False, default="v1"
    )
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    request_id: Mapped[str | None] = mapped_column(String(255))
    signature_state: Mapped[str | None] = mapped_column(String(120))
    reason_code: Mapped[str | None] = mapped_column(String(128))
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "provider", "idempotency_key", name="uq_webhook_events_provider_idempotency"
        ),
        UniqueConstraint(
            "provider", "event_id", name="uq_webhook_events_provider_event_id"
        ),
        Index("ix_webhook_events_processed_created", "processed", "created_at"),
        Index("ix_webhook_events_signature_state", "signature_state"),
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(
        SqlEnum(OutboxStatus),
        nullable=False,
        default=OutboxStatus.PENDING,
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (Index("ix_outbox_events_status", "status", "retry_count"),)
