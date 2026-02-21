from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from godlife_backend.adapter.webapi.dependencies import get_plan_service
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
    GeneratePlanCommand,
)
from pydantic import BaseModel

router = APIRouter(prefix="/plans", tags=["plans"])


class GeneratePlanRequest(BaseModel):
    user_id: UUID
    target_date: date
    source: str = "rule"


class PlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    target_date: date
    source: str
    status: str


@router.post("/generate", response_model=PlanResponse)
def generate_plan(
    request: GeneratePlanRequest,
    service: Annotated[ExercisePlanService, Depends(get_plan_service)],
) -> PlanResponse:
    try:
        plan = service.generate_plan(
            GeneratePlanCommand(
                user_id=request.user_id,
                target_date=request.target_date,
                source=request.source,
            )
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    return PlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        target_date=plan.target_date,
        source=plan.source,
        status=str(plan.status),
    )
