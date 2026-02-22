from __future__ import annotations

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from godlife_backend.adapter.webapi.dependencies import get_reading_reminder_service
from godlife_backend.application.services.reading_reminder_service import (
    ReadingPlanNotFoundError,
    ReadingReminderService,
    ReadingReminderValidationError,
    ScheduleDailyReminderCommand,
    ScheduleRetryReminderCommand,
)
from pydantic import BaseModel

router = APIRouter(prefix="/reading", tags=["reading"])


class BaseReminderRequest(BaseModel):
    user_id: UUID
    reference_date: date
    idempotency_key: str | None = None


class RetryReminderRequest(BaseModel):
    user_id: UUID
    reference_date: date
    base_notification_id: UUID
    idempotency_key: str | None = None


class ReminderResponse(BaseModel):
    result: str
    notification_id: UUID | None
    schedule_at: datetime | None


@router.post(
    "/reminders/base",
    response_model=ReminderResponse,
    status_code=status.HTTP_200_OK,
)
def create_base_reminder(
    request: BaseReminderRequest,
    service: Annotated[ReadingReminderService, Depends(get_reading_reminder_service)],
) -> ReminderResponse:
    try:
        outcome = service.schedule_daily_reminder(
            ScheduleDailyReminderCommand(
                user_id=request.user_id,
                reference_date=request.reference_date,
                idempotency_key=request.idempotency_key,
            )
        )
    except ReadingPlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReadingReminderValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    notification = outcome.notification
    return ReminderResponse(
        result=outcome.result,
        notification_id=notification.id if notification is not None else None,
        schedule_at=notification.schedule_at if notification is not None else None,
    )


@router.post(
    "/reminders/retry",
    response_model=ReminderResponse,
    status_code=status.HTTP_200_OK,
)
def create_retry_reminder(
    request: RetryReminderRequest,
    service: Annotated[ReadingReminderService, Depends(get_reading_reminder_service)],
) -> ReminderResponse:
    try:
        outcome = service.schedule_retry_if_incomplete(
            ScheduleRetryReminderCommand(
                user_id=request.user_id,
                reference_date=request.reference_date,
                base_notification_id=request.base_notification_id,
                idempotency_key=request.idempotency_key,
            )
        )
    except ReadingPlanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReadingReminderValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    notification = outcome.notification
    return ReminderResponse(
        result=outcome.result,
        notification_id=notification.id if notification is not None else None,
        schedule_at=notification.schedule_at if notification is not None else None,
    )
