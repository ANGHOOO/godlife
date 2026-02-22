from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from uuid import uuid4

import pytest
from godlife_backend.adapter.test_doubles import (
    InMemoryNotificationRepository,
    InMemoryOutboxEventRepository,
    InMemoryReadingLogRepository,
    InMemoryReadingPlanRepository,
)
from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from godlife_backend.application.services.reading_reminder_service import (
    ReadingPlanNotFoundError,
    ReadingReminderService,
    ScheduleDailyReminderCommand,
    ScheduleRetryReminderCommand,
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


def test_schedule_daily_reminder_creates_and_deduplicates(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    user_id = uuid4()
    reference_date = date(2026, 2, 22)
    reading_plan_repository.save(
        ReadingPlan(
            user_id=user_id,
            remind_time=time(20, 30),
            enabled=True,
        )
    )

    first = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(user_id=user_id, reference_date=reference_date)
    )
    second = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(user_id=user_id, reference_date=reference_date)
    )

    assert first.result == "created"
    assert first.notification is not None
    assert first.notification.kind == "READING_REMINDER"
    assert first.notification.schedule_at == datetime(
        2026,
        2,
        22,
        20,
        30,
        tzinfo=UTC,
    )

    assert second.result == "duplicate"
    assert second.notification is not None
    assert second.notification.id == first.notification.id


def test_schedule_retry_if_incomplete_creates_once(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    user_id = uuid4()
    reference_date = date(2026, 2, 22)
    reading_plan_repository.save(
        ReadingPlan(
            user_id=user_id,
            remind_time=time(9, 0),
            enabled=True,
        )
    )
    base = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(user_id=user_id, reference_date=reference_date)
    )
    assert base.notification is not None

    first_retry = service.schedule_retry_if_incomplete(
        ScheduleRetryReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
            base_notification_id=base.notification.id,
        )
    )
    second_retry = service.schedule_retry_if_incomplete(
        ScheduleRetryReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
            base_notification_id=base.notification.id,
        )
    )

    assert first_retry.result == "created"
    assert first_retry.notification is not None
    assert first_retry.notification.kind == "READING_REMINDER_RETRY"
    expected_retry_schedule_at = base.notification.schedule_at + timedelta(minutes=30)
    assert first_retry.notification.schedule_at == expected_retry_schedule_at

    assert second_retry.result == "duplicate"
    assert second_retry.notification is not None
    assert second_retry.notification.id == first_retry.notification.id


@pytest.mark.parametrize(
    "status",
    [ReadingLogStatus.DONE, ReadingLogStatus.SKIPPED],
)
def test_schedule_retry_skips_when_done_or_skipped_exists(
    status: ReadingLogStatus,
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, reading_log_repository = service_bundle
    user_id = uuid4()
    reference_date = date(2026, 2, 22)
    plan = reading_plan_repository.save(
        ReadingPlan(
            user_id=user_id,
            remind_time=time(7, 0),
            enabled=True,
        )
    )
    base = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(user_id=user_id, reference_date=reference_date)
    )
    assert base.notification is not None
    reading_log_repository.save(
        ReadingLog(
            user_id=user_id,
            reading_plan_id=plan.id,
            status=status,
            created_at=datetime(2026, 2, 22, 8, 0, tzinfo=UTC),
        )
    )

    retry = service.schedule_retry_if_incomplete(
        ScheduleRetryReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
            base_notification_id=base.notification.id,
        )
    )

    assert retry.result == "skipped_completed"
    assert retry.notification is None


def test_schedule_daily_reminder_raises_when_plan_missing(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, _, _ = service_bundle

    with pytest.raises(ReadingPlanNotFoundError):
        service.schedule_daily_reminder(
            ScheduleDailyReminderCommand(
                user_id=uuid4(),
                reference_date=date(2026, 2, 22),
            )
        )
