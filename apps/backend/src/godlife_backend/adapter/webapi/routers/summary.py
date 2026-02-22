from __future__ import annotations

from datetime import date
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from godlife_backend.adapter.webapi.dependencies import get_summary_service
from godlife_backend.application.services.summary_service import SummaryService
from pydantic import BaseModel

router = APIRouter(prefix="/summary", tags=["summary"])


class DailySummaryResponse(BaseModel):
    user_id: UUID
    date: date
    exercise_completion_rate: float
    reading_completed: bool
    streak_days: int
    trend: str


class DailyPointResponse(BaseModel):
    date: date
    exercise_completion_rate: float
    reading_completed: bool


class WeeklySummaryResponse(BaseModel):
    user_id: UUID
    start_date: date
    end_date: date
    daily_points: list[DailyPointResponse]
    week_avg_completion_rate: float
    streak_days: int
    trend: str


def _to_daily_point_response(point: dict[str, object]) -> DailyPointResponse:
    return DailyPointResponse(
        date=date.fromisoformat(cast(str, point["date"])),
        exercise_completion_rate=float(
            cast(float | int | str, point["exercise_completion_rate"])
        ),
        reading_completed=bool(cast(bool, point["reading_completed"])),
    )


@router.get(
    "/daily", response_model=DailySummaryResponse, status_code=status.HTTP_200_OK
)
def get_daily_summary(
    user_id: Annotated[UUID, Query()],
    date_value: Annotated[date, Query(alias="date")],
    service: Annotated[SummaryService, Depends(get_summary_service)],
) -> DailySummaryResponse:
    summary = service.get_daily_summary(user_id=user_id, target_date=date_value)
    return DailySummaryResponse(
        user_id=summary.user_id,
        date=summary.summary_date,
        exercise_completion_rate=summary.exercise_completion_rate,
        reading_completed=summary.reading_completed,
        streak_days=summary.streak_days,
        trend=summary.trend,
    )


@router.get(
    "/weekly",
    response_model=WeeklySummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_weekly_summary(
    user_id: Annotated[UUID, Query()],
    start_date: Annotated[date, Query(alias="start_date")],
    service: Annotated[SummaryService, Depends(get_summary_service)],
) -> WeeklySummaryResponse:
    summary = service.get_weekly_summary(user_id=user_id, start_date=start_date)
    return WeeklySummaryResponse(
        user_id=summary.user_id,
        start_date=summary.start_date,
        end_date=summary.end_date,
        daily_points=[
            _to_daily_point_response(point) for point in summary.daily_points
        ],
        week_avg_completion_rate=summary.week_avg_completion_rate,
        streak_days=summary.streak_days,
        trend=summary.trend,
    )
