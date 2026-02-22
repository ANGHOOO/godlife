from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from godlife_backend.adapter.webapi.dependencies import (
    get_plan_service,
    get_webhook_service,
)
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
    SetContextMismatchError,
    SetOrderViolationError,
    SetResultCommand,
    SetResultValidationError,
)
from godlife_backend.application.services.webhook_service import WebhookService
from godlife_backend.domain.entities import WebhookEvent
from pydantic import BaseModel, Field

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookPayload(BaseModel):
    provider: str
    event_type: str
    user_id: UUID | None = None
    event_id: str | None = None
    idempotency_key: str | None = None
    plan_id: UUID | None = None
    session_id: UUID | None = None
    set_no: int | None = Field(default=None, ge=1)
    result: str | None = None
    performed_reps: int | None = Field(default=None, ge=0)
    performed_weight_kg: float | None = Field(default=None, ge=0)
    actual_rest_sec: int | None = Field(default=None, ge=0)
    raw_payload: dict[str, object] = Field(default_factory=dict)


@router.post("/{provider}")
def ingest_webhook(
    provider: str,
    payload: WebhookPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
    plan_service: Annotated[ExercisePlanService, Depends(get_plan_service)],
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
        idempotency_key=(
            payload.idempotency_key
            or (
                f"{provider}:{payload.event_type}:{payload.event_id}"
                if payload.event_id is not None
                else f"{provider}:{payload.event_type}"
            )
        ),
        raw_payload=payload.raw_payload,
    )

    saved_event = service.handle_event(event)
    is_duplicate = saved_event.id != event.id
    if is_duplicate:
        return {"result": "duplicate"}

    has_set_result_context = (
        payload.plan_id is not None
        and payload.session_id is not None
        and payload.set_no is not None
        and payload.result is not None
    )
    if has_set_result_context:
        try:
            plan_service.submit_set_result(
                SetResultCommand(
                    plan_id=payload.plan_id,  # type: ignore[arg-type]
                    session_id=payload.session_id,  # type: ignore[arg-type]
                    set_no=payload.set_no,  # type: ignore[arg-type]
                    result=payload.result,  # type: ignore[arg-type]
                    performed_reps=payload.performed_reps,
                    performed_weight_kg=payload.performed_weight_kg,
                    actual_rest_sec=payload.actual_rest_sec,
                )
            )
        except SetResultValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except SetContextMismatchError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except SetOrderViolationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {"result": "accepted"}
