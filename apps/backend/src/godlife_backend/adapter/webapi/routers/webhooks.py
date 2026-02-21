from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from godlife_backend.adapter.webapi.dependencies import get_webhook_service
from godlife_backend.application.services.webhook_service import WebhookService
from godlife_backend.domain.entities import WebhookEvent
from pydantic import BaseModel, Field

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookPayload(BaseModel):
    provider: str
    event_type: str
    user_id: UUID | None = None
    event_id: str | None = None
    raw_payload: dict[str, object] = Field(default_factory=dict)


@router.post("/{provider}")
def ingest_webhook(
    provider: str,
    payload: WebhookPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
) -> dict[str, str]:
    if payload.provider != provider:
        raise HTTPException(
            status_code=400,
            detail="provider mismatch between path and body",
        )

    event = WebhookEvent(
        provider=provider,
        event_type=payload.event_type,
        user_id=payload.user_id,
        event_id=payload.event_id,
        idempotency_key=f"{provider}:{payload.event_type}:{payload.event_id}"
        if payload.event_id is not None
        else f"{provider}:{payload.event_type}",
        raw_payload=payload.raw_payload,
    )

    try:
        service.handle_event(event)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    return {"result": "accepted"}
