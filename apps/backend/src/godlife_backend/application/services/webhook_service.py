"""Webhook use-case skeleton for PR-01."""

from __future__ import annotations

from godlife_backend.domain.entities import WebhookEvent
from godlife_backend.domain.ports import OutboxEventRepository, WebhookEventRepository


class WebhookService:
    def __init__(
        self,
        webhook_event_repository: WebhookEventRepository,
        outbox_repository: OutboxEventRepository,
    ) -> None:
        self._webhook_event_repository = webhook_event_repository
        self._outbox_repository = outbox_repository

    def handle_event(self, event: WebhookEvent) -> WebhookEvent:
        raise NotImplementedError(
            "PR-01: Webhook handler use case is not implemented yet."
        )

    def replay_failed_events(
        self, *, provider: str, limit: int = 50
    ) -> list[WebhookEvent]:
        return []

    @property
    def repositories(self) -> tuple:
        return (self._webhook_event_repository, self._outbox_repository)
