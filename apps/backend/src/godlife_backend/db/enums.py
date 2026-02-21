from __future__ import annotations

from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class PlanStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    CANCELED = "CANCELED"


class SetStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class ReadingLogStatus(StrEnum):
    DONE = "DONE"
    SKIPPED = "SKIPPED"
    ABANDONED = "ABANDONED"


class NotificationStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class OutboxStatus(StrEnum):
    PENDING = "PENDING"
    IN_FLIGHT = "IN_FLIGHT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

