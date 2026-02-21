"""Domain entities for the GodLife backend skeleton."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from uuid import UUID, uuid4

from godlife_backend.db.enums import (
    NotificationStatus,
    OutboxStatus,
    PlanStatus,
    ReadingLogStatus,
    SetStatus,
    UserStatus,
)


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class User:
    id: UUID = field(default_factory=uuid4)
    kakao_user_id: str = ""
    name: str = ""
    timezone: str = "Asia/Seoul"
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class UserProfile:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    age: int | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    goal: str | None = None
    experience_level: str | None = None
    max_daily_minutes: int | None = None
    available_equipment: str | None = None
    injury_notes: str | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class ExercisePlan:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    target_date: date = field(default_factory=date.today)
    source: str = "rule"
    status: PlanStatus = PlanStatus.DRAFT
    summary: str | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class ExerciseSession:
    id: UUID = field(default_factory=uuid4)
    plan_id: UUID = field(default_factory=uuid4)
    order_no: int = 0
    exercise_name: str = ""
    body_part: str | None = None
    target_sets: int = 0
    target_reps: int | None = None
    target_weight_kg: float | None = None
    target_rest_sec: int | None = None
    notes: str | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class ExerciseSetState:
    id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    set_no: int = 0
    status: SetStatus = SetStatus.PENDING
    performed_reps: int | None = None
    performed_weight_kg: float | None = None
    actual_rest_sec: int | None = None
    completed_at: datetime | None = None
    skipped_at: datetime | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class ReadingPlan:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    remind_time: time = time(9, 0)
    goal_minutes: int = 30
    enabled: bool = True
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class ReadingLog:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    reading_plan_id: UUID | None = None
    book_title: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    pages_read: int | None = None
    status: ReadingLogStatus = ReadingLogStatus.DONE
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class Notification:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    kind: str = ""
    related_id: UUID | None = None
    status: NotificationStatus = NotificationStatus.SCHEDULED
    schedule_at: datetime = field(default_factory=_now)
    sent_at: datetime | None = None
    retry_count: int = 0
    idempotency_key: str = ""
    payload: dict[str, object] = field(default_factory=dict)
    reason_code: str | None = None
    provider_response_code: str | None = None
    failure_reason: str | None = None
    last_error_at: datetime | None = None
    memo: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class NotificationProviderCode:
    id: UUID = field(default_factory=uuid4)
    notification_id: UUID = field(default_factory=uuid4)
    provider: str = ""
    provider_status_code: str = ""
    provider_response: str | None = None
    captured_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class WebhookEvent:
    id: UUID = field(default_factory=uuid4)
    provider: str = ""
    event_type: str = ""
    user_id: UUID | None = None
    idempotency_key: str = ""
    event_id: str | None = None
    schema_version: str = "v1"
    request_id: str | None = None
    signature_state: str | None = None
    raw_payload: dict[str, object] = field(default_factory=dict)
    processed: bool = False
    reason_code: str | None = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=_now)


@dataclass(slots=True)
class OutboxEvent:
    id: UUID = field(default_factory=uuid4)
    aggregate_type: str = ""
    aggregate_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    payload: dict[str, object] = field(default_factory=dict)
    status: OutboxStatus = OutboxStatus.PENDING
    retry_count: int = 0
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
