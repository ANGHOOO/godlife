"""FastAPI dependency wiring for services and sessions."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from godlife_backend.adapter.persistence.repositories.sqlalchemy_repositories import (
    SqlAlchemyExercisePlanRepository,
    SqlAlchemyExerciseSessionRepository,
    SqlAlchemyExerciseSetStateRepository,
    SqlAlchemyNotificationRepository,
    SqlAlchemyOutboxEventRepository,
    SqlAlchemyWebhookEventRepository,
)
from godlife_backend.adapter.persistence.session import get_session
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
)
from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from godlife_backend.application.services.webhook_service import WebhookService
from sqlalchemy.orm import Session

SessionDep = Annotated[Session, Depends(get_session)]


def get_plan_service(session: SessionDep) -> ExercisePlanService:
    return ExercisePlanService(
        plan_repository=SqlAlchemyExercisePlanRepository(session),
        session_repository=SqlAlchemyExerciseSessionRepository(session),
        set_state_repository=SqlAlchemyExerciseSetStateRepository(session),
        outbox_repository=SqlAlchemyOutboxEventRepository(session),
    )


def get_notification_service(session: SessionDep) -> NotificationService:
    return NotificationService(
        notification_repository=SqlAlchemyNotificationRepository(session),
        outbox_repository=SqlAlchemyOutboxEventRepository(session),
    )


def get_webhook_service(session: SessionDep) -> WebhookService:
    return WebhookService(
        webhook_event_repository=SqlAlchemyWebhookEventRepository(session),
        outbox_repository=SqlAlchemyOutboxEventRepository(session),
    )
