"""Notification use-case skeleton for PR-01."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from godlife_backend.db.enums import NotificationStatus
from godlife_backend.domain.entities import Notification, OutboxEvent
from godlife_backend.domain.ports import NotificationRepository, OutboxEventRepository


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
        outbox_repository: OutboxEventRepository,
    ) -> None:
        self._notification_repository = notification_repository
        self._outbox_repository = outbox_repository

    def create_pending_notification(
        self,
        *,
        user_id: UUID,
        kind: str,
        related_id: UUID | None,
        schedule_at: datetime,
        idempotency_key: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> Notification:
        key = idempotency_key or (
            f"notification:{kind}:{user_id}:{related_id}:{schedule_at.isoformat()}"
        )
        existing = self._notification_repository.get_by_idempotency_key(key)
        if existing is not None:
            return existing

        notification = Notification(
            user_id=user_id,
            kind=kind,
            related_id=related_id,
            status=NotificationStatus.SCHEDULED,
            schedule_at=schedule_at,
            idempotency_key=key,
            payload=payload or {},
        )
        saved = self._notification_repository.save(notification)
        self._outbox_repository.save(
            OutboxEvent(
                aggregate_type="notification",
                aggregate_id=saved.id,
                event_type="NotificationScheduled",
                payload={
                    "notification_id": str(saved.id),
                    "kind": saved.kind,
                    "schedule_at": saved.schedule_at.isoformat(),
                },
            )
        )
        return saved

    def mark_as_retried(self, notification_id: UUID) -> Notification | None:
        notification = self._notification_repository.get_by_id(notification_id)
        if notification is None:
            return None
        notification.retry_count += 1
        notification.status = NotificationStatus.RETRY_SCHEDULED
        notification.schedule_at = datetime.now(UTC)
        saved = self._notification_repository.save(notification)
        self._outbox_repository.save(
            OutboxEvent(
                aggregate_type="notification",
                aggregate_id=saved.id,
                event_type="NotificationRetryScheduled",
                payload={
                    "notification_id": str(saved.id),
                    "retry_count": saved.retry_count,
                },
            )
        )
        return saved

    @property
    def repositories(self) -> tuple:
        return (self._notification_repository, self._outbox_repository)
