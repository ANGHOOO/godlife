"""SQLAlchemy repository implementations for domain ports."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from uuid import UUID

from godlife_backend.db.enums import NotificationStatus, PlanStatus
from godlife_backend.domain.entities import (
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
)
from godlife_backend.domain.ports import (
    ExercisePlanRepository,
    ExerciseSessionRepository,
    ExerciseSetStateRepository,
    NotificationRepository,
    OutboxEventRepository,
    ReadingLogRepository,
    ReadingPlanRepository,
    UserProfileRepository,
    UserRepository,
    WebhookEventRepository,
)
from sqlalchemy.orm import Session


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError("SQLAlchemy User repository not implemented yet.")

    def get_by_kakao_user_id(self, kakao_user_id: str) -> User | None:
        raise NotImplementedError("SQLAlchemy User repository not implemented yet.")

    def save(self, user: User) -> User:
        raise NotImplementedError("SQLAlchemy User repository not implemented yet.")


class SqlAlchemyUserProfileRepository(UserProfileRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        raise NotImplementedError(
            "SQLAlchemy UserProfile repository not implemented yet."
        )

    def save(self, profile: UserProfile) -> UserProfile:
        raise NotImplementedError(
            "SQLAlchemy UserProfile repository not implemented yet."
        )


class SqlAlchemyExercisePlanRepository(ExercisePlanRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_by_user_and_date(
        self, user_id: UUID, target_date: date
    ) -> ExercisePlan | None:
        raise NotImplementedError(
            "SQLAlchemy ExercisePlan repository not implemented yet."
        )

    def get_by_id(self, plan_id: UUID) -> ExercisePlan | None:
        raise NotImplementedError(
            "SQLAlchemy ExercisePlan repository not implemented yet."
        )

    def list_by_user(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        status: PlanStatus | None = None,
    ) -> list[ExercisePlan]:
        raise NotImplementedError(
            "SQLAlchemy ExercisePlan repository not implemented yet."
        )

    def save(self, plan: ExercisePlan) -> ExercisePlan:
        raise NotImplementedError(
            "SQLAlchemy ExercisePlan repository not implemented yet."
        )


class SqlAlchemyExerciseSessionRepository(ExerciseSessionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_plan(self, plan_id: UUID) -> list[ExerciseSession]:
        raise NotImplementedError(
            "SQLAlchemy ExerciseSession repository not implemented yet."
        )

    def get_by_id(self, session_id: UUID) -> ExerciseSession | None:
        raise NotImplementedError(
            "SQLAlchemy ExerciseSession repository not implemented yet."
        )

    def save(self, session: ExerciseSession) -> ExerciseSession:
        raise NotImplementedError(
            "SQLAlchemy ExerciseSession repository not implemented yet."
        )


class SqlAlchemyExerciseSetStateRepository(ExerciseSetStateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, session_id: UUID, set_no: int) -> ExerciseSetState | None:
        raise NotImplementedError(
            "SQLAlchemy ExerciseSetState repository not implemented yet."
        )

    def list_pending(self, session_id: UUID) -> list[ExerciseSetState]:
        raise NotImplementedError(
            "SQLAlchemy ExerciseSetState repository not implemented yet."
        )

    def save(self, state: ExerciseSetState) -> ExerciseSetState:
        raise NotImplementedError(
            "SQLAlchemy ExerciseSetState repository not implemented yet."
        )


class SqlAlchemyReadingPlanRepository(ReadingPlanRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user(self, user_id: UUID) -> ReadingPlan | None:
        raise NotImplementedError(
            "SQLAlchemy ReadingPlan repository not implemented yet."
        )

    def save(self, plan: ReadingPlan) -> ReadingPlan:
        raise NotImplementedError(
            "SQLAlchemy ReadingPlan repository not implemented yet."
        )


class SqlAlchemyReadingLogRepository(ReadingLogRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Sequence[ReadingLog]:
        raise NotImplementedError(
            "SQLAlchemy ReadingLog repository not implemented yet."
        )

    def get_by_id(self, log_id: UUID) -> ReadingLog | None:
        raise NotImplementedError(
            "SQLAlchemy ReadingLog repository not implemented yet."
        )

    def save(self, log: ReadingLog) -> ReadingLog:
        raise NotImplementedError(
            "SQLAlchemy ReadingLog repository not implemented yet."
        )


class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, notification_id: UUID) -> Notification | None:
        raise NotImplementedError(
            "SQLAlchemy Notification repository not implemented yet."
        )

    def get_by_idempotency_key(self, idempotency_key: str) -> Notification | None:
        raise NotImplementedError(
            "SQLAlchemy Notification repository not implemented yet."
        )

    def list(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        from_at: date | None = None,
        to_at: date | None = None,
    ) -> Sequence[Notification]:
        raise NotImplementedError(
            "SQLAlchemy Notification repository not implemented yet."
        )

    def save(self, notification: Notification) -> Notification:
        raise NotImplementedError(
            "SQLAlchemy Notification repository not implemented yet."
        )


class SqlAlchemyWebhookEventRepository(WebhookEventRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_provider_and_key(self, provider: str, key: str) -> WebhookEvent | None:
        raise NotImplementedError(
            "SQLAlchemy WebhookEvent repository not implemented yet."
        )

    def save(self, event: WebhookEvent) -> WebhookEvent:
        raise NotImplementedError(
            "SQLAlchemy WebhookEvent repository not implemented yet."
        )

    def get_by_provider_and_event_id(
        self, provider: str, event_id: str
    ) -> WebhookEvent | None:
        raise NotImplementedError(
            "SQLAlchemy WebhookEvent repository not implemented yet."
        )

    def mark_failed(self, event_id: UUID, reason: str | None) -> WebhookEvent | None:
        raise NotImplementedError(
            "SQLAlchemy WebhookEvent repository not implemented yet."
        )


class SqlAlchemyOutboxEventRepository(OutboxEventRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def lease_pending(self, limit: int = 100) -> list[OutboxEvent]:
        raise NotImplementedError(
            "SQLAlchemy OutboxEvent repository not implemented yet."
        )

    def save(self, event: OutboxEvent) -> OutboxEvent:
        raise NotImplementedError(
            "SQLAlchemy OutboxEvent repository not implemented yet."
        )

    def mark_complete(self, event_id: UUID) -> OutboxEvent | None:
        raise NotImplementedError(
            "SQLAlchemy OutboxEvent repository not implemented yet."
        )

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        raise NotImplementedError(
            "SQLAlchemy OutboxEvent repository not implemented yet."
        )
