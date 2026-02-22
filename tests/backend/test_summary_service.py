from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from godlife_backend.adapter.test_doubles import (
    InMemorySummaryRepository,
    InMemoryUserRepository,
)
from godlife_backend.application.services.summary_service import SummaryService
from godlife_backend.domain.entities import User


def test_recompute_daily_calculates_completion_streak_and_trend() -> None:
    summary_repository = InMemorySummaryRepository()
    user_repository = InMemoryUserRepository()
    user = user_repository.save(
        User(id=uuid4(), name="tester", kakao_user_id="kakao-1")
    )
    service = SummaryService(
        summary_repository=summary_repository,
        user_repository=user_repository,
    )

    summary_repository.seed_exercise(
        user_id=user.id,
        summary_date=date(2026, 3, 2),
        total_sets=8,
        done_sets=2,
    )
    summary_repository.seed_exercise(
        user_id=user.id,
        summary_date=date(2026, 3, 3),
        total_sets=8,
        done_sets=6,
    )

    summary = service.recompute_daily(user_id=user.id, summary_date=date(2026, 3, 3))

    assert summary.exercise_completion_rate == 0.75
    assert summary.streak_days == 2
    assert summary.trend == "up"
    assert summary.reading_completed is False


def test_recompute_daily_uses_reading_completion_for_activity_streak() -> None:
    summary_repository = InMemorySummaryRepository()
    user_repository = InMemoryUserRepository()
    user = user_repository.save(
        User(id=uuid4(), name="tester", kakao_user_id="kakao-2")
    )
    service = SummaryService(
        summary_repository=summary_repository,
        user_repository=user_repository,
    )

    summary_repository.seed_reading_completion(
        user_id=user.id,
        completed_at=datetime(2026, 3, 1, 16, 10, tzinfo=UTC),
    )
    summary_repository.seed_reading_completion(
        user_id=user.id,
        completed_at=datetime(2026, 3, 2, 16, 30, tzinfo=UTC),
    )

    summary = service.recompute_daily(user_id=user.id, summary_date=date(2026, 3, 3))

    assert summary.exercise_completion_rate == 0.0
    assert summary.reading_completed is True
    assert summary.streak_days == 2


def test_recompute_daily_falls_back_to_default_timezone_when_invalid_timezone() -> None:
    summary_repository = InMemorySummaryRepository()
    user_repository = InMemoryUserRepository()
    user = user_repository.save(
        User(
            id=uuid4(),
            name="tester",
            kakao_user_id="kakao-3",
            timezone="Invalid/Timezone",
        )
    )
    service = SummaryService(
        summary_repository=summary_repository,
        user_repository=user_repository,
    )

    summary_repository.seed_reading_completion(
        user_id=user.id,
        completed_at=datetime(2026, 3, 3, 16, 0, tzinfo=UTC),
    )

    summary = service.recompute_daily(user_id=user.id, summary_date=date(2026, 3, 4))

    assert summary.timezone == "Asia/Seoul"
    assert summary.reading_completed is True


def test_recompute_weekly_returns_daily_points_and_weekly_trend() -> None:
    summary_repository = InMemorySummaryRepository()
    user_repository = InMemoryUserRepository()
    user = user_repository.save(
        User(id=uuid4(), name="tester", kakao_user_id="kakao-4")
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
            total_sets=4,
            done_sets=4,
        )
        summary_repository.seed_exercise(
            user_id=user.id,
            summary_date=start_date - timedelta(days=7) + timedelta(days=offset),
            total_sets=4,
            done_sets=0,
        )

    weekly = service.recompute_weekly(user_id=user.id, start_date=start_date)

    assert len(weekly.daily_points) == 7
    assert weekly.week_avg_completion_rate == 1.0
    assert weekly.trend == "up"
    assert weekly.streak_days == 7
