"""SQLAlchemy repository implementations for domain ports."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime
from uuid import UUID

from godlife_backend.db import models as persistence_models
from godlife_backend.db.enums import (
    NotificationStatus,
    OutboxStatus,
    PlanStatus,
    SetStatus,
)
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
from sqlalchemy import select
from sqlalchemy.orm import Session


def _to_domain_exercise_plan(model: persistence_models.ExercisePlan) -> ExercisePlan:
    return ExercisePlan(
        id=model.id,
        user_id=model.user_id,
        target_date=model.target_date,
        source=model.source,
        status=model.status,
        summary=model.summary,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_exercise_session(
    model: persistence_models.ExerciseSession,
) -> ExerciseSession:
    return ExerciseSession(
        id=model.id,
        plan_id=model.plan_id,
        order_no=model.order_no,
        exercise_name=model.exercise_name,
        body_part=model.body_part,
        target_sets=model.target_sets,
        target_reps=model.target_reps,
        target_weight_kg=model.target_weight_kg,
        target_rest_sec=model.target_rest_sec,
        notes=model.notes,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_exercise_set_state(
    model: persistence_models.ExerciseSetState,
) -> ExerciseSetState:
    return ExerciseSetState(
        id=model.id,
        session_id=model.session_id,
        set_no=model.set_no,
        status=model.status,
        performed_reps=model.performed_reps,
        performed_weight_kg=model.performed_weight_kg,
        actual_rest_sec=model.actual_rest_sec,
        completed_at=model.completed_at,
        skipped_at=model.skipped_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_reading_plan(model: persistence_models.ReadingPlan) -> ReadingPlan:
    return ReadingPlan(
        id=model.id,
        user_id=model.user_id,
        remind_time=model.remind_time,
        goal_minutes=model.goal_minutes,
        enabled=model.enabled,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_reading_log(model: persistence_models.ReadingLog) -> ReadingLog:
    return ReadingLog(
        id=model.id,
        user_id=model.user_id,
        reading_plan_id=model.reading_plan_id,
        book_title=model.book_title,
        start_at=model.start_at,
        end_at=model.end_at,
        pages_read=model.pages_read,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_notification(model: persistence_models.Notification) -> Notification:
    return Notification(
        id=model.id,
        user_id=model.user_id,
        kind=model.kind,
        related_id=model.related_id,
        status=model.status,
        schedule_at=model.schedule_at,
        sent_at=model.sent_at,
        retry_count=model.retry_count,
        idempotency_key=model.idempotency_key,
        payload=model.payload,
        reason_code=model.reason_code,
        provider_response_code=model.provider_response_code,
        failure_reason=model.failure_reason,
        last_error_at=model.last_error_at,
        memo=model.memo,
        reviewed_by=model.reviewed_by,
        reviewed_at=model.reviewed_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_webhook_event(model: persistence_models.WebhookEvent) -> WebhookEvent:
    return WebhookEvent(
        id=model.id,
        provider=model.provider,
        event_type=model.event_type,
        user_id=model.user_id,
        idempotency_key=model.idempotency_key,
        event_id=model.event_id,
        schema_version=model.schema_version,
        request_id=model.request_id,
        signature_state=model.signature_state,
        raw_payload=model.raw_payload,
        processed=model.processed,
        reason_code=model.reason_code,
        retry_count=model.retry_count,
        created_at=model.created_at,
    )


def _to_domain_outbox_event(model: persistence_models.OutboxEvent) -> OutboxEvent:
    return OutboxEvent(
        id=model.id,
        aggregate_type=model.aggregate_type,
        aggregate_id=model.aggregate_id,
        event_type=model.event_type,
        payload=model.payload,
        status=model.status,
        retry_count=model.retry_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


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
        statement = select(persistence_models.ExercisePlan).where(
            persistence_models.ExercisePlan.user_id == user_id,
            persistence_models.ExercisePlan.target_date == target_date,
            persistence_models.ExercisePlan.status == PlanStatus.ACTIVE,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _to_domain_exercise_plan(model)

    def get_by_id(self, plan_id: UUID) -> ExercisePlan | None:
        model = self._session.get(persistence_models.ExercisePlan, plan_id)
        if model is None:
            return None
        return _to_domain_exercise_plan(model)

    def list_by_user(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        status: PlanStatus | None = None,
    ) -> list[ExercisePlan]:
        statement = select(persistence_models.ExercisePlan).where(
            persistence_models.ExercisePlan.user_id == user_id
        )
        if from_date is not None:
            statement = statement.where(
                persistence_models.ExercisePlan.target_date >= from_date
            )
        if to_date is not None:
            statement = statement.where(
                persistence_models.ExercisePlan.target_date <= to_date
            )
        if status is not None:
            statement = statement.where(
                persistence_models.ExercisePlan.status == status
            )
        statement = statement.order_by(
            persistence_models.ExercisePlan.created_at.desc()
        )
        models = self._session.scalars(statement).all()
        return [_to_domain_exercise_plan(model) for model in models]

    def save(self, plan: ExercisePlan) -> ExercisePlan:
        model = self._session.get(persistence_models.ExercisePlan, plan.id)
        if model is None:
            model = persistence_models.ExercisePlan(
                id=plan.id,
                user_id=plan.user_id,
                target_date=plan.target_date,
                source=plan.source,
                status=plan.status,
                summary=plan.summary,
            )
            self._session.add(model)
        else:
            model.user_id = plan.user_id
            model.target_date = plan.target_date
            model.source = plan.source
            model.status = plan.status
            model.summary = plan.summary
        self._session.flush()
        return _to_domain_exercise_plan(model)


class SqlAlchemyExerciseSessionRepository(ExerciseSessionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_plan(self, plan_id: UUID) -> list[ExerciseSession]:
        statement = (
            select(persistence_models.ExerciseSession)
            .where(persistence_models.ExerciseSession.plan_id == plan_id)
            .order_by(persistence_models.ExerciseSession.order_no.asc())
        )
        models = self._session.scalars(statement).all()
        return [_to_domain_exercise_session(model) for model in models]

    def get_by_id(self, session_id: UUID) -> ExerciseSession | None:
        model = self._session.get(persistence_models.ExerciseSession, session_id)
        if model is None:
            return None
        return _to_domain_exercise_session(model)

    def save(self, session: ExerciseSession) -> ExerciseSession:
        model = self._session.get(persistence_models.ExerciseSession, session.id)
        if model is None:
            model = persistence_models.ExerciseSession(
                id=session.id,
                plan_id=session.plan_id,
                order_no=session.order_no,
                exercise_name=session.exercise_name,
                body_part=session.body_part,
                target_sets=session.target_sets,
                target_reps=session.target_reps,
                target_weight_kg=session.target_weight_kg,
                target_rest_sec=session.target_rest_sec,
                notes=session.notes,
            )
            self._session.add(model)
        else:
            model.plan_id = session.plan_id
            model.order_no = session.order_no
            model.exercise_name = session.exercise_name
            model.body_part = session.body_part
            model.target_sets = session.target_sets
            model.target_reps = session.target_reps
            model.target_weight_kg = session.target_weight_kg
            model.target_rest_sec = session.target_rest_sec
            model.notes = session.notes
        self._session.flush()
        return _to_domain_exercise_session(model)


class SqlAlchemyExerciseSetStateRepository(ExerciseSetStateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, session_id: UUID, set_no: int) -> ExerciseSetState | None:
        statement = select(persistence_models.ExerciseSetState).where(
            persistence_models.ExerciseSetState.session_id == session_id,
            persistence_models.ExerciseSetState.set_no == set_no,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _to_domain_exercise_set_state(model)

    def list_pending(self, session_id: UUID) -> list[ExerciseSetState]:
        statement = (
            select(persistence_models.ExerciseSetState)
            .where(
                persistence_models.ExerciseSetState.session_id == session_id,
                persistence_models.ExerciseSetState.status == SetStatus.PENDING,
            )
            .order_by(persistence_models.ExerciseSetState.set_no.asc())
        )
        models = self._session.scalars(statement).all()
        return [_to_domain_exercise_set_state(model) for model in models]

    def save(self, state: ExerciseSetState) -> ExerciseSetState:
        model = self._session.get(persistence_models.ExerciseSetState, state.id)
        if model is None:
            model = persistence_models.ExerciseSetState(
                id=state.id,
                session_id=state.session_id,
                set_no=state.set_no,
                status=state.status,
                performed_reps=state.performed_reps,
                performed_weight_kg=state.performed_weight_kg,
                actual_rest_sec=state.actual_rest_sec,
                completed_at=state.completed_at,
                skipped_at=state.skipped_at,
            )
            self._session.add(model)
        else:
            model.session_id = state.session_id
            model.set_no = state.set_no
            model.status = state.status
            model.performed_reps = state.performed_reps
            model.performed_weight_kg = state.performed_weight_kg
            model.actual_rest_sec = state.actual_rest_sec
            model.completed_at = state.completed_at
            model.skipped_at = state.skipped_at
        self._session.flush()
        return _to_domain_exercise_set_state(model)


class SqlAlchemyReadingPlanRepository(ReadingPlanRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user(self, user_id: UUID) -> ReadingPlan | None:
        statement = (
            select(persistence_models.ReadingPlan)
            .where(persistence_models.ReadingPlan.user_id == user_id)
            .order_by(persistence_models.ReadingPlan.created_at.desc())
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _to_domain_reading_plan(model)

    def save(self, plan: ReadingPlan) -> ReadingPlan:
        model = self._session.get(persistence_models.ReadingPlan, plan.id)
        if model is None:
            model = persistence_models.ReadingPlan(
                id=plan.id,
                user_id=plan.user_id,
                remind_time=plan.remind_time,
                goal_minutes=plan.goal_minutes,
                enabled=plan.enabled,
            )
            self._session.add(model)
        else:
            model.user_id = plan.user_id
            model.remind_time = plan.remind_time
            model.goal_minutes = plan.goal_minutes
            model.enabled = plan.enabled
        self._session.flush()
        return _to_domain_reading_plan(model)


class SqlAlchemyReadingLogRepository(ReadingLogRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Sequence[ReadingLog]:
        statement = select(persistence_models.ReadingLog).where(
            persistence_models.ReadingLog.user_id == user_id
        )
        if from_date is not None:
            statement = statement.where(
                persistence_models.ReadingLog.created_at
                >= datetime.combine(from_date, datetime.min.time(), tzinfo=UTC)
            )
        if to_date is not None:
            statement = statement.where(
                persistence_models.ReadingLog.created_at
                <= datetime.combine(to_date, datetime.max.time(), tzinfo=UTC)
            )
        statement = statement.order_by(persistence_models.ReadingLog.created_at.desc())
        models = self._session.scalars(statement).all()
        return [_to_domain_reading_log(model) for model in models]

    def get_by_id(self, log_id: UUID) -> ReadingLog | None:
        model = self._session.get(persistence_models.ReadingLog, log_id)
        if model is None:
            return None
        return _to_domain_reading_log(model)

    def save(self, log: ReadingLog) -> ReadingLog:
        model = self._session.get(persistence_models.ReadingLog, log.id)
        if model is None:
            model = persistence_models.ReadingLog(
                id=log.id,
                user_id=log.user_id,
                reading_plan_id=log.reading_plan_id,
                book_title=log.book_title,
                start_at=log.start_at,
                end_at=log.end_at,
                pages_read=log.pages_read,
                status=log.status,
            )
            self._session.add(model)
        else:
            model.user_id = log.user_id
            model.reading_plan_id = log.reading_plan_id
            model.book_title = log.book_title
            model.start_at = log.start_at
            model.end_at = log.end_at
            model.pages_read = log.pages_read
            model.status = log.status
        self._session.flush()
        return _to_domain_reading_log(model)


class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, notification_id: UUID) -> Notification | None:
        model = self._session.get(persistence_models.Notification, notification_id)
        if model is None:
            return None
        return _to_domain_notification(model)

    def get_by_idempotency_key(self, idempotency_key: str) -> Notification | None:
        statement = select(persistence_models.Notification).where(
            persistence_models.Notification.idempotency_key == idempotency_key
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _to_domain_notification(model)

    def list(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        from_at: date | None = None,
        to_at: date | None = None,
    ) -> Sequence[Notification]:
        statement = select(persistence_models.Notification).where(
            persistence_models.Notification.user_id == user_id
        )
        if status is not None:
            statement = statement.where(
                persistence_models.Notification.status == status
            )
        if from_at is not None:
            statement = statement.where(
                persistence_models.Notification.schedule_at
                >= datetime.combine(from_at, datetime.min.time(), tzinfo=UTC)
            )
        if to_at is not None:
            statement = statement.where(
                persistence_models.Notification.schedule_at
                <= datetime.combine(to_at, datetime.max.time(), tzinfo=UTC)
            )
        statement = statement.order_by(
            persistence_models.Notification.schedule_at.desc()
        )
        models = self._session.scalars(statement).all()
        return [_to_domain_notification(model) for model in models]

    def save(self, notification: Notification) -> Notification:
        model = self._session.get(persistence_models.Notification, notification.id)
        if model is None:
            model = persistence_models.Notification(
                id=notification.id,
                user_id=notification.user_id,
                kind=notification.kind,
                related_id=notification.related_id,
                status=notification.status,
                schedule_at=notification.schedule_at,
                sent_at=notification.sent_at,
                retry_count=notification.retry_count,
                idempotency_key=notification.idempotency_key,
                payload=notification.payload,
                reason_code=notification.reason_code,
                provider_response_code=notification.provider_response_code,
                failure_reason=notification.failure_reason,
                last_error_at=notification.last_error_at,
                memo=notification.memo,
                reviewed_by=notification.reviewed_by,
                reviewed_at=notification.reviewed_at,
            )
            self._session.add(model)
        else:
            model.user_id = notification.user_id
            model.kind = notification.kind
            model.related_id = notification.related_id
            model.status = notification.status
            model.schedule_at = notification.schedule_at
            model.sent_at = notification.sent_at
            model.retry_count = notification.retry_count
            model.idempotency_key = notification.idempotency_key
            model.payload = notification.payload
            model.reason_code = notification.reason_code
            model.provider_response_code = notification.provider_response_code
            model.failure_reason = notification.failure_reason
            model.last_error_at = notification.last_error_at
            model.memo = notification.memo
            model.reviewed_by = notification.reviewed_by
            model.reviewed_at = notification.reviewed_at
        self._session.flush()
        return _to_domain_notification(model)


class SqlAlchemyWebhookEventRepository(WebhookEventRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_provider_and_key(self, provider: str, key: str) -> WebhookEvent | None:
        statement = select(persistence_models.WebhookEvent).where(
            persistence_models.WebhookEvent.provider == provider,
            persistence_models.WebhookEvent.idempotency_key == key,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _to_domain_webhook_event(model)

    def save(self, event: WebhookEvent) -> WebhookEvent:
        model = self._session.get(persistence_models.WebhookEvent, event.id)
        if model is None:
            model = persistence_models.WebhookEvent(
                id=event.id,
                provider=event.provider,
                event_type=event.event_type,
                user_id=event.user_id,
                idempotency_key=event.idempotency_key,
                event_id=event.event_id,
                schema_version=event.schema_version,
                request_id=event.request_id,
                signature_state=event.signature_state,
                raw_payload=event.raw_payload,
                processed=event.processed,
                reason_code=event.reason_code,
                retry_count=event.retry_count,
            )
            self._session.add(model)
        else:
            model.provider = event.provider
            model.event_type = event.event_type
            model.user_id = event.user_id
            model.idempotency_key = event.idempotency_key
            model.event_id = event.event_id
            model.schema_version = event.schema_version
            model.request_id = event.request_id
            model.signature_state = event.signature_state
            model.raw_payload = event.raw_payload
            model.processed = event.processed
            model.reason_code = event.reason_code
            model.retry_count = event.retry_count
        self._session.flush()
        return _to_domain_webhook_event(model)

    def get_by_provider_and_event_id(
        self, provider: str, event_id: str
    ) -> WebhookEvent | None:
        statement = select(persistence_models.WebhookEvent).where(
            persistence_models.WebhookEvent.provider == provider,
            persistence_models.WebhookEvent.event_id == event_id,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _to_domain_webhook_event(model)

    def mark_failed(self, event_id: UUID, reason: str | None) -> WebhookEvent | None:
        model = self._session.get(persistence_models.WebhookEvent, event_id)
        if model is None:
            return None
        model.reason_code = reason
        model.retry_count += 1
        model.processed = False
        self._session.flush()
        return _to_domain_webhook_event(model)


class SqlAlchemyOutboxEventRepository(OutboxEventRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def lease_pending(self, limit: int = 100) -> list[OutboxEvent]:
        statement = (
            select(persistence_models.OutboxEvent)
            .where(persistence_models.OutboxEvent.status == OutboxStatus.PENDING)
            .order_by(persistence_models.OutboxEvent.created_at.asc())
            .limit(limit)
        )
        models = self._session.scalars(statement).all()
        return [_to_domain_outbox_event(model) for model in models]

    def save(self, event: OutboxEvent) -> OutboxEvent:
        model = self._session.get(persistence_models.OutboxEvent, event.id)
        if model is None:
            model = persistence_models.OutboxEvent(
                id=event.id,
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                event_type=event.event_type,
                payload=event.payload,
                status=event.status,
                retry_count=event.retry_count,
            )
            self._session.add(model)
        else:
            model.aggregate_type = event.aggregate_type
            model.aggregate_id = event.aggregate_id
            model.event_type = event.event_type
            model.payload = event.payload
            model.status = event.status
            model.retry_count = event.retry_count
        self._session.flush()
        return _to_domain_outbox_event(model)

    def mark_complete(self, event_id: UUID) -> OutboxEvent | None:
        model = self._session.get(persistence_models.OutboxEvent, event_id)
        if model is None:
            return None
        model.status = OutboxStatus.COMPLETED
        self._session.flush()
        return _to_domain_outbox_event(model)

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        model = self._session.get(persistence_models.OutboxEvent, event_id)
        if model is None:
            return None
        model.status = OutboxStatus.FAILED
        model.retry_count += 1
        if reason is not None:
            model.payload = {**model.payload, "failure_reason": reason}
        self._session.flush()
        return _to_domain_outbox_event(model)
