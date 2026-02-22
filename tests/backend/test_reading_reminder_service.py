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
    ReadingReminderValidationError,
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


def test_schedule_retry_rejects_non_base_notification_kind(
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
        ReadingPlan(user_id=user_id, remind_time=time(9, 0), enabled=True)
    )
    base = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
        )
    )
    assert base.notification is not None
    base.notification.kind = "EXERCISE_START"

    with pytest.raises(ReadingReminderValidationError):
        service.schedule_retry_if_incomplete(
            ScheduleRetryReminderCommand(
                user_id=user_id,
                reference_date=reference_date,
                base_notification_id=base.notification.id,
            )
        )


def test_schedule_retry_rejects_mismatched_reference_date(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    user_id = uuid4()
    reading_plan_repository.save(
        ReadingPlan(user_id=user_id, remind_time=time(9, 0), enabled=True)
    )
    base = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(
            user_id=user_id,
            reference_date=date(2026, 2, 21),
        )
    )
    assert base.notification is not None

    with pytest.raises(ReadingReminderValidationError):
        service.schedule_retry_if_incomplete(
            ScheduleRetryReminderCommand(
                user_id=user_id,
                reference_date=date(2026, 2, 22),
                base_notification_id=base.notification.id,
            )
        )


def test_schedule_daily_rejects_cross_user_idempotency_key_reuse(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    reference_date = date(2026, 2, 22)
    user1 = uuid4()
    user2 = uuid4()
    shared_key = "shared-base-key"
    reading_plan_repository.save(
        ReadingPlan(user_id=user1, remind_time=time(9, 0), enabled=True)
    )
    reading_plan_repository.save(
        ReadingPlan(user_id=user2, remind_time=time(10, 0), enabled=True)
    )
    first = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(
            user_id=user1,
            reference_date=reference_date,
            idempotency_key=shared_key,
        )
    )
    assert first.result == "created"

    with pytest.raises(ReadingReminderValidationError):
        service.schedule_daily_reminder(
            ScheduleDailyReminderCommand(
                user_id=user2,
                reference_date=reference_date,
                idempotency_key=shared_key,
            )
        )


def test_schedule_daily_returns_duplicate_before_plan_disabled_check(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    user_id = uuid4()
    reference_date = date(2026, 2, 22)
    key = "stable-idempotency-key"
    plan = reading_plan_repository.save(
        ReadingPlan(user_id=user_id, remind_time=time(9, 0), enabled=True)
    )
    first = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
            idempotency_key=key,
        )
    )
    assert first.result == "created"
    plan.enabled = False

    second = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
            idempotency_key=key,
        )
    )

    assert second.result == "duplicate"
    assert second.notification is not None
    assert first.notification is not None
    assert second.notification.id == first.notification.id


def test_schedule_retry_rejects_cross_user_idempotency_key_reuse(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, _ = service_bundle
    reference_date = date(2026, 2, 22)
    user1 = uuid4()
    user2 = uuid4()
    shared_key = "shared-retry-key"
    reading_plan_repository.save(
        ReadingPlan(user_id=user1, remind_time=time(9, 0), enabled=True)
    )
    reading_plan_repository.save(
        ReadingPlan(user_id=user2, remind_time=time(10, 0), enabled=True)
    )
    base1 = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(user_id=user1, reference_date=reference_date)
    )
    base2 = service.schedule_daily_reminder(
        ScheduleDailyReminderCommand(user_id=user2, reference_date=reference_date)
    )
    assert base1.notification is not None
    assert base2.notification is not None
    first_retry = service.schedule_retry_if_incomplete(
        ScheduleRetryReminderCommand(
            user_id=user1,
            reference_date=reference_date,
            base_notification_id=base1.notification.id,
            idempotency_key=shared_key,
        )
    )
    assert first_retry.result == "created"

    with pytest.raises(ReadingReminderValidationError):
        service.schedule_retry_if_incomplete(
            ScheduleRetryReminderCommand(
                user_id=user2,
                reference_date=reference_date,
                base_notification_id=base2.notification.id,
                idempotency_key=shared_key,
            )
        )


def test_schedule_retry_returns_duplicate_before_done_check(
    service_bundle: tuple[
        ReadingReminderService,
        InMemoryReadingPlanRepository,
        InMemoryReadingLogRepository,
    ],
) -> None:
    service, reading_plan_repository, reading_log_repository = service_bundle
    user_id = uuid4()
    reference_date = date(2026, 2, 22)
    retry_key = "stable-retry-key"
    plan = reading_plan_repository.save(
        ReadingPlan(user_id=user_id, remind_time=time(9, 0), enabled=True)
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
            idempotency_key=retry_key,
        )
    )
    assert first_retry.result == "created"
    reading_log_repository.save(
        ReadingLog(
            user_id=user_id,
            reading_plan_id=plan.id,
            status=ReadingLogStatus.DONE,
            created_at=datetime(2026, 2, 22, 10, 0, tzinfo=UTC),
        )
    )

    second_retry = service.schedule_retry_if_incomplete(
        ScheduleRetryReminderCommand(
            user_id=user_id,
            reference_date=reference_date,
            base_notification_id=base.notification.id,
            idempotency_key=retry_key,
        )
    )

    assert second_retry.result == "duplicate"
    assert second_retry.notification is not None
    assert first_retry.notification is not None
    assert second_retry.notification.id == first_retry.notification.id
