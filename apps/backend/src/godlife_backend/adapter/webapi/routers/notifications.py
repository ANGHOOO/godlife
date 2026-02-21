from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from godlife_backend.adapter.webapi.dependencies import get_notification_service
from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["notifications"])


class RetryNotificationRequest(BaseModel):
    notification_id: UUID


class NotificationStatusResponse(BaseModel):
    id: UUID
    state: str


@router.post("/retry", response_model=NotificationStatusResponse)
def retry_notification(
    request: RetryNotificationRequest,
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> NotificationStatusResponse:
    try:
        notification = service.mark_as_retried(request.notification_id)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    if notification is None:
        raise HTTPException(status_code=404, detail="notification not found")

    return NotificationStatusResponse(
        id=notification.id, state=str(notification.status)
    )
