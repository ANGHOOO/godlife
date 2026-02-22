from __future__ import annotations

from datetime import UTC, date, datetime, time
from uuid import uuid4

import pytest
from fastapi import HTTPException
from godlife_backend.adapter.test_doubles import (
    InMemoryNotificationRepository,
    InMemoryOutboxEventRepository,
    InMemoryReadingLogRepository,
    InMemoryReadingPlanRepository,
)
from godlife_backend.adapter.webapi.routers.reading import (
    BaseReminderRequest,
    ReminderResponse,
    RetryReminderRequest,
    create_base_reminder,
    create_retry_reminder,
)
from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from godlife_backend.application.services.reading_reminder_service import (
    ReadingReminderService,
)
from godlife_backend.db.enums import ReadingLogStatus
from godlife_backend.domain.entities import ReadingLog, ReadingPlan


@pytest.fixture()
def service_bundle() -> tuple[
    ReadingReminderService,
    InMemoryReadingPlanRepository,
    InMemoryReadingLogRepository,
]:
    reading_plan_repository = InMemoryReadingPlanRepository()
    reading_log_repository = InMemoryReadingLogRepository()
    notification_repository = InMemoryNotificationRepository()
    service = ReadingReminderService(
        reading_plan_repository=reading_plan_repository,
        reading_log_repository=reading_log_repository,
        notification_repository=notification_repository,
        notification_service=NotificationService(
            notification_repository=notification_repository,
            outbox_repository=InMemoryOutboxEventRepository(),
        ),
    )
    return service, reading_plan_repository, reading_log_repository


def test_create_base_reminder_returns_notification(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    user_id = uuid4()
    reading_plan_repository.save(
        ReadingPlan(
            user_id=user_id,
            remind_time=time(21, 0),
            enabled=True,
        )
    )

    response = create_base_reminder(
        request=BaseReminderRequest(
            user_id=user_id,
            reference_date=date(2026, 2, 22),
        ),
        service=service,
    )

    assert isinstance(response, ReminderResponse)
    assert response.result == "created"
    assert response.notification_id is not None
    assert response.schedule_at == datetime(2026, 2, 22, 21, 0, tzinfo=UTC)


def test_create_retry_reminder_skips_when_reading_done(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, reading_log_repository = service_bundle
    user_id = uuid4()
    plan = reading_plan_repository.save(
        ReadingPlan(
            user_id=user_id,
            remind_time=time(21, 0),
            enabled=True,
        )
    )
    base = create_base_reminder(
        request=BaseReminderRequest(
            user_id=user_id,
            reference_date=date(2026, 2, 22),
        ),
        service=service,
    )
    assert base.notification_id is not None
    reading_log_repository.save(
        ReadingLog(
            user_id=user_id,
            reading_plan_id=plan.id,
            status=ReadingLogStatus.DONE,
            created_at=datetime(2026, 2, 22, 22, 0, tzinfo=UTC),
        )
    )

    response = create_retry_reminder(
        request=RetryReminderRequest(
            user_id=user_id,
            reference_date=date(2026, 2, 22),
            base_notification_id=base.notification_id,
        ),
        service=service,
    )

    assert response.result == "skipped_completed"
    assert response.notification_id is None
    assert response.schedule_at is None


def test_create_base_reminder_returns_404_for_missing_plan(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, _, _ = service_bundle

    with pytest.raises(HTTPException) as exc_info:
        create_base_reminder(
            request=BaseReminderRequest(
                user_id=uuid4(),
                reference_date=date(2026, 2, 22),
            ),
            service=service,
        )

    assert exc_info.value.status_code == 404
