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
)
from pydantic import BaseModel

router = APIRouter(prefix="/plans", tags=["plans"])


class GeneratePlanRequest(BaseModel):
    user_id: UUID
    target_date: date
    plan_source: str | None = None
    source: str | None = None

    def resolved_source(self) -> str:
        if self.plan_source:
            return self.plan_source
        if self.source:
            return self.source
        return "rule"


class PlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    target_date: date
    source: str
    status: str


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
