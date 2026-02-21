"""Notification use-case skeleton for PR-01."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from godlife_backend.domain.entities import Notification
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
    ) -> Notification:
        raise NotImplementedError(
            "PR-01: Notification creation use case is not implemented yet."
        )

    def mark_as_retried(self, notification_id: UUID) -> Notification | None:
        notification = self._notification_repository.get_by_id(notification_id)
        if notification is None:
            return None
        raise NotImplementedError(
            "PR-01: Notification retry mutation is not implemented yet."
        )

    @property
    def repositories(self) -> tuple:
        return (self._notification_repository, self._outbox_repository)
