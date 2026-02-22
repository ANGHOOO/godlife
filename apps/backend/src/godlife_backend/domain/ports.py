"""Port interfaces for application/persistence decoupling."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from godlife_backend.db.enums import NotificationStatus, PlanStatus
from godlife_backend.domain.entities import (
    DailySummary,
    ExercisePlan,
    ExerciseSession,
    ExerciseSetState,
    Notification,
    OutboxEvent,
    ReadingLog,
    ReadingPlan,
    User,
    UserProfile,
    WebhookEvent,
    WeeklySummary,
)


class UserRepository(Protocol):
    def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    def get_by_kakao_user_id(self, kakao_user_id: str) -> User | None:
        raise NotImplementedError

    def save(self, user: User) -> User:
        raise NotImplementedError


class UserProfileRepository(Protocol):
    def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        raise NotImplementedError

    def save(self, profile: UserProfile) -> UserProfile:
        raise NotImplementedError


class ExercisePlanRepository(Protocol):
    def get_active_by_user_and_date(
        self,
        user_id: UUID,
        target_date: date,
    ) -> ExercisePlan | None:
        raise NotImplementedError

    def get_by_id(self, plan_id: UUID) -> ExercisePlan | None:
        raise NotImplementedError

    def list_by_user(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        status: PlanStatus | None = None,
    ) -> list[ExercisePlan]:
        raise NotImplementedError

    def save(self, plan: ExercisePlan) -> ExercisePlan:
        raise NotImplementedError


class ExerciseSessionRepository(Protocol):
    def list_by_plan(self, plan_id: UUID) -> list[ExerciseSession]:
        raise NotImplementedError

    def get_by_id(self, session_id: UUID) -> ExerciseSession | None:
        raise NotImplementedError

    def save(self, session: ExerciseSession) -> ExerciseSession:
        raise NotImplementedError


class ExerciseSetStateRepository(Protocol):
    def get(self, session_id: UUID, set_no: int) -> ExerciseSetState | None:
        raise NotImplementedError

    def list_pending(self, session_id: UUID) -> list[ExerciseSetState]:
        raise NotImplementedError

    def save(self, state: ExerciseSetState) -> ExerciseSetState:
        raise NotImplementedError


class ReadingPlanRepository(Protocol):
    def get_by_user(self, user_id: UUID) -> ReadingPlan | None:
        raise NotImplementedError

    def save(self, plan: ReadingPlan) -> ReadingPlan:
        raise NotImplementedError


class ReadingLogRepository(Protocol):
    def list(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Sequence[ReadingLog]:
        raise NotImplementedError

    def get_by_id(self, log_id: UUID) -> ReadingLog | None:
        raise NotImplementedError

    def save(self, log: ReadingLog) -> ReadingLog:
        raise NotImplementedError


class NotificationRepository(Protocol):
    def get_by_id(self, notification_id: UUID) -> Notification | None:
        raise NotImplementedError

    def get_by_idempotency_key(self, idempotency_key: str) -> Notification | None:
        raise NotImplementedError

    def list(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        from_at: date | None = None,
        to_at: date | None = None,
    ) -> Sequence[Notification]:
        raise NotImplementedError

    def save(self, notification: Notification) -> Notification:
        raise NotImplementedError


class WebhookEventRepository(Protocol):
    def get_by_provider_and_key(self, provider: str, key: str) -> WebhookEvent | None:
        raise NotImplementedError

    def save(self, event: WebhookEvent) -> WebhookEvent:
        raise NotImplementedError

    def get_by_provider_and_event_id(
        self, provider: str, event_id: str
    ) -> WebhookEvent | None:
        raise NotImplementedError

    def mark_failed(self, event_id: UUID, reason: str | None) -> WebhookEvent | None:
        raise NotImplementedError


class OutboxEventRepository(Protocol):
    def lease_pending(self, limit: int = 100) -> list[OutboxEvent]:
        raise NotImplementedError

    def save(self, event: OutboxEvent) -> OutboxEvent:
        raise NotImplementedError

    def mark_complete(self, event_id: UUID) -> OutboxEvent | None:
        raise NotImplementedError

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        raise NotImplementedError


class SummaryRepository(Protocol):
    def get_daily(self, user_id: UUID, summary_date: date) -> DailySummary | None:
        raise NotImplementedError

    def upsert_daily(self, summary: DailySummary) -> DailySummary:
        raise NotImplementedError

    def get_weekly(self, user_id: UUID, start_date: date) -> WeeklySummary | None:
        raise NotImplementedError

    def upsert_weekly(self, summary: WeeklySummary) -> WeeklySummary:
        raise NotImplementedError

    def aggregate_exercise_sets(
        self, user_id: UUID, summary_date: date
    ) -> tuple[int, int]:
        raise NotImplementedError

    def has_reading_completion(
        self,
        user_id: UUID,
        window_start_utc: datetime,
        window_end_utc: datetime,
    ) -> bool:
        raise NotImplementedError
