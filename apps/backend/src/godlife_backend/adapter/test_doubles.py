"""In-memory repository doubles for local tests and offline development."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from godlife_backend.db.enums import (
    NotificationStatus,
    OutboxStatus,
    PlanStatus,
    SetStatus,
)
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
from godlife_backend.domain.ports import (
    ExercisePlanRepository,
    ExerciseSessionRepository,
    ExerciseSetStateRepository,
    NotificationRepository,
    OutboxEventRepository,
    ReadingLogRepository,
    ReadingPlanRepository,
    SummaryRepository,
    UserProfileRepository,
    UserRepository,
    WebhookEventRepository,
)


class _HasId(Protocol):
    id: UUID


@dataclass
class _IndexedStore[U: _HasId]:
    entities: dict[UUID, U] = field(default_factory=dict)

    def upsert(self, entity: U) -> None:
        self.entities[entity.id] = entity

    def list_all(self) -> list[U]:
        return list(self.entities.values())


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[User]()

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._store.entities.get(user_id)

    def get_by_kakao_user_id(self, kakao_user_id: str) -> User | None:
        for user in self._store.list_all():
            if user.kakao_user_id == kakao_user_id:
                return user
        return None

    def save(self, user: User) -> User:
        self._store.upsert(user)
        return user


class InMemoryUserProfileRepository(UserProfileRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[UserProfile]()

    def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        for profile in self._store.list_all():
            if profile.user_id == user_id:
                return profile
        return None

    def save(self, profile: UserProfile) -> UserProfile:
        self._store.upsert(profile)
        return profile


class InMemoryExercisePlanRepository(ExercisePlanRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[ExercisePlan]()

    def get_active_by_user_and_date(
        self, user_id: UUID, target_date: date
    ) -> ExercisePlan | None:
        for plan in self._store.list_all():
            if (
                plan.user_id == user_id
                and plan.target_date == target_date
                and plan.status == PlanStatus.ACTIVE
            ):
                return plan
        return None

    def get_by_id(self, plan_id: UUID) -> ExercisePlan | None:
        return self._store.entities.get(plan_id)

    def list_by_user(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        status: PlanStatus | None = None,
    ) -> list[ExercisePlan]:
        plans: list[ExercisePlan] = [
            plan
            for plan in self._store.list_all()
            if plan.user_id == user_id and (status is None or plan.status == status)
        ]
        if from_date is not None:
            plans = [plan for plan in plans if plan.target_date >= from_date]
        if to_date is not None:
            plans = [plan for plan in plans if plan.target_date <= to_date]
        plans.sort(key=lambda plan: plan.created_at, reverse=True)
        return plans

    def save(self, plan: ExercisePlan) -> ExercisePlan:
        self._store.upsert(plan)
        return plan


class InMemoryExerciseSessionRepository(ExerciseSessionRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[ExerciseSession]()

    def list_by_plan(self, plan_id: UUID) -> list[ExerciseSession]:
        return sorted(
            [
                session
                for session in self._store.list_all()
                if session.plan_id == plan_id
            ],
            key=lambda session: session.order_no,
        )

    def get_by_id(self, session_id: UUID) -> ExerciseSession | None:
        return self._store.entities.get(session_id)

    def save(self, session: ExerciseSession) -> ExerciseSession:
        self._store.upsert(session)
        return session


class InMemoryExerciseSetStateRepository(ExerciseSetStateRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[ExerciseSetState]()

    def get(self, session_id: UUID, set_no: int) -> ExerciseSetState | None:
        for state in self._store.list_all():
            if state.session_id == session_id and state.set_no == set_no:
                return state
        return None

    def list_pending(self, session_id: UUID) -> list[ExerciseSetState]:
        pending: list[ExerciseSetState] = [
            state
            for state in self._store.list_all()
            if state.session_id == session_id and state.status == SetStatus.PENDING
        ]
        return sorted(pending, key=lambda state: state.set_no)

    def save(self, state: ExerciseSetState) -> ExerciseSetState:
        self._store.upsert(state)
        return state


class InMemoryReadingPlanRepository(ReadingPlanRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[ReadingPlan]()

    def get_by_user(self, user_id: UUID) -> ReadingPlan | None:
        for plan in self._store.list_all():
            if plan.user_id == user_id:
                return plan
        return None

    def save(self, plan: ReadingPlan) -> ReadingPlan:
        self._store.upsert(plan)
        return plan


class InMemoryReadingLogRepository(ReadingLogRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[ReadingLog]()

    def list(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Sequence[ReadingLog]:
        logs: list[ReadingLog] = [
            log for log in self._store.list_all() if log.user_id == user_id
        ]
        if from_date is not None:
            logs = [log for log in logs if log.created_at.date() >= from_date]
        if to_date is not None:
            logs = [log for log in logs if log.created_at.date() <= to_date]
        logs.sort(key=lambda log: log.created_at, reverse=True)
        return logs

    def get_by_id(self, log_id: UUID) -> ReadingLog | None:
        return self._store.entities.get(log_id)

    def save(self, log: ReadingLog) -> ReadingLog:
        self._store.upsert(log)
        return log


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[Notification]()

    def get_by_id(self, notification_id: UUID) -> Notification | None:
        return self._store.entities.get(notification_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> Notification | None:
        for notification in self._store.list_all():
            if notification.idempotency_key == idempotency_key:
                return notification
        return None

    def list(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        from_at: date | None = None,
        to_at: date | None = None,
    ) -> Sequence[Notification]:
        notifications: list[Notification] = [
            notification
            for notification in self._store.list_all()
            if notification.user_id == user_id
        ]
        if status is not None:
            notifications = [n for n in notifications if n.status == status]
        if from_at is not None:
            notifications = [
                n for n in notifications if n.schedule_at.date() >= from_at
            ]
        if to_at is not None:
            notifications = [n for n in notifications if n.schedule_at.date() <= to_at]
        notifications.sort(key=lambda n: n.schedule_at, reverse=True)
        return notifications

    def save(self, notification: Notification) -> Notification:
        self._store.upsert(notification)
        return notification


class InMemoryWebhookEventRepository(WebhookEventRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[WebhookEvent]()

    def get_by_provider_and_key(self, provider: str, key: str) -> WebhookEvent | None:
        for event in self._store.list_all():
            if event.provider == provider and event.idempotency_key == key:
                return event
        return None

    def save(self, event: WebhookEvent) -> WebhookEvent:
        self._store.upsert(event)
        return event

    def get_by_provider_and_event_id(
        self, provider: str, event_id: str
    ) -> WebhookEvent | None:
        for event in self._store.list_all():
            if event.provider == provider and event.event_id == event_id:
                return event
        return None

    def mark_failed(self, event_id: UUID, reason: str | None) -> WebhookEvent | None:
        event = self._store.entities.get(event_id)
        if event is None:
            return None
        if reason is not None:
            event.reason_code = reason
        return event


class InMemoryOutboxEventRepository(OutboxEventRepository):
    def __init__(self) -> None:
        self._store = _IndexedStore[OutboxEvent]()

    def lease_pending(self, limit: int = 100) -> list[OutboxEvent]:
        events = [
            event
            for event in self._store.list_all()
            if event.status == OutboxStatus.PENDING
        ]
        return sorted(events, key=lambda event: event.created_at)[:limit]

    def save(self, event: OutboxEvent) -> OutboxEvent:
        self._store.upsert(event)
        return event

    def mark_complete(self, event_id: UUID) -> OutboxEvent | None:
        event = self._store.entities.get(event_id)
        if event is None:
            return None
        event.status = OutboxStatus.COMPLETED
        return event

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        event = self._store.entities.get(event_id)
        if event is None:
            return None
        if reason is not None:
            event.payload = {**event.payload, "failure_reason": reason}
        event.status = OutboxStatus.FAILED
        return event


class InMemorySummaryRepository(SummaryRepository):
    def __init__(self) -> None:
        self._daily_store = _IndexedStore[DailySummary]()
        self._weekly_store = _IndexedStore[WeeklySummary]()
        self._daily_key_to_id: dict[tuple[UUID, date], UUID] = {}
        self._weekly_key_to_id: dict[tuple[UUID, date], UUID] = {}
        self._exercise_source: dict[tuple[UUID, date], tuple[int, int]] = {}
        self._reading_source: dict[UUID, list[datetime]] = {}

    def get_daily(self, user_id: UUID, summary_date: date) -> DailySummary | None:
        summary_id = self._daily_key_to_id.get((user_id, summary_date))
        if summary_id is None:
            return None
        return self._daily_store.entities.get(summary_id)

    def upsert_daily(self, summary: DailySummary) -> DailySummary:
        existing_id = self._daily_key_to_id.get((summary.user_id, summary.summary_date))
        if existing_id is not None:
            summary.id = existing_id
        self._daily_store.upsert(summary)
        self._daily_key_to_id[(summary.user_id, summary.summary_date)] = summary.id
        return summary

    def get_weekly(self, user_id: UUID, start_date: date) -> WeeklySummary | None:
        summary_id = self._weekly_key_to_id.get((user_id, start_date))
        if summary_id is None:
            return None
        return self._weekly_store.entities.get(summary_id)

    def upsert_weekly(self, summary: WeeklySummary) -> WeeklySummary:
        existing_id = self._weekly_key_to_id.get((summary.user_id, summary.start_date))
        if existing_id is not None:
            summary.id = existing_id
        self._weekly_store.upsert(summary)
        self._weekly_key_to_id[(summary.user_id, summary.start_date)] = summary.id
        return summary

    def aggregate_exercise_sets(
        self, user_id: UUID, summary_date: date
    ) -> tuple[int, int]:
        return self._exercise_source.get((user_id, summary_date), (0, 0))

    def has_reading_completion(
        self,
        user_id: UUID,
        window_start_utc: datetime,
        window_end_utc: datetime,
    ) -> bool:
        completions = self._reading_source.get(user_id, [])
        return any(window_start_utc <= item <= window_end_utc for item in completions)

    def seed_exercise(
        self, *, user_id: UUID, summary_date: date, total_sets: int, done_sets: int
    ) -> None:
        self._exercise_source[(user_id, summary_date)] = (total_sets, done_sets)

    def seed_reading_completion(self, *, user_id: UUID, completed_at: datetime) -> None:
        self._reading_source.setdefault(user_id, []).append(completed_at)
