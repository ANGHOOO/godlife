from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from godlife_backend.adapter.test_doubles import (
    InMemorySummaryRepository,
    InMemoryUserRepository,
)
from godlife_backend.adapter.webapi.routers.summary import (
    DailySummaryResponse,
    WeeklySummaryResponse,
    get_daily_summary,
    get_weekly_summary,
)
from godlife_backend.application.services.summary_service import SummaryService
from godlife_backend.domain.entities import User


def test_get_daily_summary_returns_contract_shape() -> None:
    summary_repository = InMemorySummaryRepository()
    user_repository = InMemoryUserRepository()
    user = user_repository.save(
        User(id=uuid4(), name="tester", kakao_user_id="kakao-5")
    )
    service = SummaryService(
        summary_repository=summary_repository,
        user_repository=user_repository,
    )
    summary_repository.seed_exercise(
        user_id=user.id,
        summary_date=date(2026, 3, 10),
        total_sets=10,
        done_sets=8,
    )

    response = get_daily_summary(
        user_id=user.id,
        date_value=date(2026, 3, 10),
        service=service,
    )

    assert isinstance(response, DailySummaryResponse)
    assert response.exercise_completion_rate == 0.8
    assert response.date == date(2026, 3, 10)


def test_get_weekly_summary_returns_daily_points_array() -> None:
    summary_repository = InMemorySummaryRepository()
    user_repository = InMemoryUserRepository()
    user = user_repository.save(
        User(id=uuid4(), name="tester", kakao_user_id="kakao-6")
    )
    service = SummaryService(
        summary_repository=summary_repository,
        user_repository=user_repository,
    )
    start_date = date(2026, 3, 8)

    for offset in range(7):
        summary_repository.seed_exercise(
            user_id=user.id,
            summary_date=start_date + timedelta(days=offset),
            total_sets=2,
            done_sets=1,
        )

    response = get_weekly_summary(
        user_id=user.id, start_date=start_date, service=service
    )

    assert isinstance(response, WeeklySummaryResponse)
    assert len(response.daily_points) == 7
    assert response.start_date == start_date
    assert response.end_date == start_date + timedelta(days=6)
