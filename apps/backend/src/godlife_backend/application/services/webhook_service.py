"""Webhook use-case skeleton for PR-01."""

from __future__ import annotations

from godlife_backend.domain.entities import OutboxEvent, WebhookEvent
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
        existing = self._webhook_event_repository.get_by_provider_and_key(
            event.provider, event.idempotency_key
        )
        if existing is not None:
            return existing
        if event.event_id is not None:
            existing_by_event_id = (
                self._webhook_event_repository.get_by_provider_and_event_id(
                    event.provider, event.event_id
                )
            )
            if existing_by_event_id is not None:
                return existing_by_event_id

        saved = self._webhook_event_repository.save(event)
        self._outbox_repository.save(
            OutboxEvent(
                aggregate_type="webhook",
                aggregate_id=saved.id,
                event_type="WebhookReceived",
                payload={
                    "provider": saved.provider,
                    "event_type": saved.event_type,
                    "event_id": saved.event_id,
                },
            )
        )
        return saved

    def replay_failed_events(
        self, *, provider: str, limit: int = 50
    ) -> list[WebhookEvent]:
        del provider, limit
        return []

    @property
    def repositories(self) -> tuple:
        return (self._webhook_event_repository, self._outbox_repository)
