from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from godlife_backend.adapter.test_doubles import (
    InMemoryExercisePlanRepository,
    InMemoryExerciseSessionRepository,
    InMemoryExerciseSetStateRepository,
    InMemoryNotificationRepository,
    InMemoryOutboxEventRepository,
    InMemoryWebhookEventRepository,
)
from godlife_backend.adapter.webapi.routers.notifications import (
    RetryNotificationRequest,
    retry_notification,
)
from godlife_backend.adapter.webapi.routers.plans import (
    GeneratePlanRequest,
    generate_plan,
)
from godlife_backend.adapter.webapi.routers.webhooks import (
    WebhookPayload,
    ingest_webhook,
)
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
)
from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from godlife_backend.application.services.webhook_service import WebhookService


@pytest.fixture()
def services() -> tuple[ExercisePlanService, NotificationService, WebhookService]:
    notification_repository = InMemoryNotificationRepository()
    outbox_repository = InMemoryOutboxEventRepository()
    plan_service = ExercisePlanService(
        plan_repository=InMemoryExercisePlanRepository(),
        session_repository=InMemoryExerciseSessionRepository(),
        set_state_repository=InMemoryExerciseSetStateRepository(),
        outbox_repository=outbox_repository,
        notification_repository=notification_repository,
    )
    notification_service = NotificationService(
        notification_repository=notification_repository,
        outbox_repository=outbox_repository,
    )
    webhook_service = WebhookService(
        webhook_event_repository=InMemoryWebhookEventRepository(),
        outbox_repository=outbox_repository,
    )
    return plan_service, notification_service, webhook_service


def test_retry_notification_updates_status(
    services: tuple[ExercisePlanService, NotificationService, WebhookService],
) -> None:
    _, notification_service, _ = services
    notification = notification_service.create_pending_notification(
        user_id=uuid4(),
        kind="EXERCISE_START",
        related_id=None,
        schedule_at=datetime.now(UTC),
        idempotency_key="retry-test-key",
    )

    response = retry_notification(
        request=RetryNotificationRequest(notification_id=notification.id),
        service=notification_service,
    )
    assert response.state == "RETRY_SCHEDULED"


def test_webhook_ingest_updates_set_and_handles_duplicate(
    services: tuple[ExercisePlanService, NotificationService, WebhookService],
) -> None:
    plan_service, _, webhook_service = services
    plan = generate_plan(
        request=GeneratePlanRequest(
            user_id=uuid4(),
            target_date=date(2026, 2, 28),
            source="rule",
        ),
        service=plan_service,
    )
    session = plan_service.repositories[1].list_by_plan(plan.id)[0]
    payload = WebhookPayload(
        provider="kakao",
        event_type="set_result",
        event_id="evt-1",
        plan_id=plan.id,
        session_id=session.id,
        set_no=1,
        result="DONE",
        performed_reps=10,
    )

    first = ingest_webhook(
        provider="kakao",
        payload=payload,
        service=webhook_service,
        plan_service=plan_service,
    )
    second = ingest_webhook(
        provider="kakao",
        payload=payload,
        service=webhook_service,
        plan_service=plan_service,
    )

    assert first["result"] == "accepted"
    assert second["result"] == "duplicate"


def test_retry_notification_not_found_returns_404(
    services: tuple[ExercisePlanService, NotificationService, WebhookService],
) -> None:
    _, notification_service, _ = services

    with pytest.raises(HTTPException) as exc_info:
        retry_notification(
            request=RetryNotificationRequest(notification_id=uuid4()),
            service=notification_service,
        )

    assert exc_info.value.status_code == 404
