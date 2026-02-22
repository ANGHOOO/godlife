"""Reading reminder/retry use-case implementation for PR-05."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Final
from uuid import UUID

from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from godlife_backend.db.enums import ReadingLogStatus
from godlife_backend.domain.entities import Notification
from godlife_backend.domain.ports import (
    NotificationRepository,
    ReadingLogRepository,
    ReadingPlanRepository,
)

READING_REMINDER_KIND: Final[str] = "READING_REMINDER"
READING_REMINDER_RETRY_KIND: Final[str] = "READING_REMINDER_RETRY"
_RETRY_DELAY_MINUTES: Final[int] = 30
_NO_RETRY_STATUSES: Final[frozenset[ReadingLogStatus]] = frozenset(
    {ReadingLogStatus.DONE, ReadingLogStatus.SKIPPED}
)


@dataclass(slots=True)
class ScheduleDailyReminderCommand:
    user_id: UUID
    reference_date: date
    idempotency_key: str | None = None


@dataclass(slots=True)
class ScheduleRetryReminderCommand:
    user_id: UUID
    reference_date: date
    base_notification_id: UUID
    idempotency_key: str | None = None


@dataclass(slots=True)
class ReadingReminderOutcome:
    result: str
    notification: Notification | None = None


class ReadingPlanNotFoundError(LookupError):
    """Raised when reading plan does not exist for user."""


class ReadingReminderValidationError(ValueError):
    """Raised when reminder scheduling preconditions are not satisfied."""


class ReadingReminderService:
    def __init__(
        self,
        reading_plan_repository: ReadingPlanRepository,
        reading_log_repository: ReadingLogRepository,
        notification_repository: NotificationRepository,
        notification_service: NotificationService,
    ) -> None:
        self._reading_plan_repository = reading_plan_repository
        self._reading_log_repository = reading_log_repository
        self._notification_repository = notification_repository
        self._notification_service = notification_service

    def schedule_daily_reminder(
        self,
        command: ScheduleDailyReminderCommand,
    ) -> ReadingReminderOutcome:
        plan = self._reading_plan_repository.get_by_user(command.user_id)
        if plan is None:
            raise ReadingPlanNotFoundError("reading plan not found")
        if not plan.enabled:
            return ReadingReminderOutcome(result="skipped_disabled")

        schedule_at = datetime.combine(
            command.reference_date,
            plan.remind_time,
            tzinfo=UTC,
        )
        key = command.idempotency_key or self._daily_idempotency_key(
            user_id=command.user_id,
            reference_date=command.reference_date,
        )
        existing = self._notification_repository.get_by_idempotency_key(key)
        if existing is not None:
            return ReadingReminderOutcome(result="duplicate", notification=existing)

        notification = self._notification_service.create_pending_notification(
            user_id=command.user_id,
            kind=READING_REMINDER_KIND,
            related_id=plan.id,
            schedule_at=schedule_at,
            idempotency_key=key,
            payload={
                "reading_plan_id": str(plan.id),
                "reference_date": command.reference_date.isoformat(),
            },
        )
        return ReadingReminderOutcome(result="created", notification=notification)

    def schedule_retry_if_incomplete(
        self,
        command: ScheduleRetryReminderCommand,
    ) -> ReadingReminderOutcome:
        plan = self._reading_plan_repository.get_by_user(command.user_id)
        if plan is None:
            raise ReadingPlanNotFoundError("reading plan not found")
        if not plan.enabled:
            return ReadingReminderOutcome(result="skipped_disabled")

        if self._has_completion_or_skip(command.user_id, command.reference_date):
            return ReadingReminderOutcome(result="skipped_completed")

        base_notification = self._notification_repository.get_by_id(
            command.base_notification_id
        )
        if base_notification is None:
            raise ReadingReminderValidationError("base notification not found")
        if base_notification.user_id != command.user_id:
            raise ReadingReminderValidationError(
                "base notification does not belong to user"
            )

        schedule_at = base_notification.schedule_at + timedelta(
            minutes=_RETRY_DELAY_MINUTES
        )
        key = command.idempotency_key or self._retry_idempotency_key(
            user_id=command.user_id,
            reference_date=command.reference_date,
        )
        existing = self._notification_repository.get_by_idempotency_key(key)
        if existing is not None:
            return ReadingReminderOutcome(result="duplicate", notification=existing)

        notification = self._notification_service.create_pending_notification(
            user_id=command.user_id,
            kind=READING_REMINDER_RETRY_KIND,
            related_id=plan.id,
            schedule_at=schedule_at,
            idempotency_key=key,
            payload={
                "reading_plan_id": str(plan.id),
                "reference_date": command.reference_date.isoformat(),
                "base_notification_id": str(command.base_notification_id),
            },
        )
        return ReadingReminderOutcome(result="created", notification=notification)

    def _has_completion_or_skip(self, user_id: UUID, reference_date: date) -> bool:
        logs = self._reading_log_repository.list(
            user_id=user_id,
            from_date=reference_date,
            to_date=reference_date,
        )
        return any(log.status in _NO_RETRY_STATUSES for log in logs)

    def _daily_idempotency_key(self, *, user_id: UUID, reference_date: date) -> str:
        return f"reading:reminder:{user_id}:{reference_date.isoformat()}"

    def _retry_idempotency_key(self, *, user_id: UUID, reference_date: date) -> str:
        return f"reading:reminder:retry:{user_id}:{reference_date.isoformat()}"
