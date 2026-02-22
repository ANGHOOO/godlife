from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from godlife_backend.adapter.webapi.dependencies import get_plan_service
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
    GeneratePlanCommand,
    InvalidPlanSourceError,
    PlanConflictError,
    SetContextMismatchError,
    SetOrderViolationError,
    SetResultCommand,
    SetResultValidationError,
)
from pydantic import BaseModel, Field

router = APIRouter(prefix="/plans", tags=["plans"])


class GeneratePlanRequest(BaseModel):
    user_id: UUID
    target_date: date
    plan_source: str | None = None
    source: str | None = None

    def resolved_source(self) -> str:
        if self.plan_source is not None:
            return self.plan_source
        if self.source is not None:
            return self.source
        return "rule"


class PlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    target_date: date
    source: str
    status: str


class SetResultRequest(BaseModel):
    result: str
    performed_reps: int | None = Field(default=None, ge=0)
    performed_weight_kg: float | None = Field(default=None, ge=0)
    actual_rest_sec: int | None = Field(default=None, ge=0)


class SetResultResponse(BaseModel):
    session_id: UUID
    set_no: int
    status: str
    next_pending_set_no: int | None
    notification_id: UUID | None


@router.post(
    "/generate",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_plan(
    request: GeneratePlanRequest,
    service: Annotated[ExercisePlanService, Depends(get_plan_service)],
) -> PlanResponse:
    try:
        plan = service.generate_plan(
            GeneratePlanCommand(
                user_id=request.user_id,
                target_date=request.target_date,
                source=request.resolved_source(),
            )
        )
    except PlanConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidPlanSourceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        target_date=plan.target_date,
        source=plan.source,
        status=plan.status.value,
    )


@router.post(
    "/{plan_id}/sessions/{session_id}/sets/{set_no}/result",
    response_model=SetResultResponse,
    status_code=status.HTTP_200_OK,
)
def submit_set_result(
    plan_id: UUID,
    session_id: UUID,
    set_no: int,
    request: SetResultRequest,
    service: Annotated[ExercisePlanService, Depends(get_plan_service)],
) -> SetResultResponse:
    try:
        outcome = service.submit_set_result(
            SetResultCommand(
                plan_id=plan_id,
                session_id=session_id,
                set_no=set_no,
                result=request.result,
                performed_reps=request.performed_reps,
                performed_weight_kg=request.performed_weight_kg,
                actual_rest_sec=request.actual_rest_sec,
            )
        )
    except SetResultValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SetContextMismatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SetOrderViolationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return SetResultResponse(
        session_id=outcome.state.session_id,
        set_no=outcome.state.set_no,
        status=outcome.state.status.value,
        next_pending_set_no=outcome.next_pending_set_no,
        notification_id=outcome.notification_id,
    )
