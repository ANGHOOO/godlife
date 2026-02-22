"""Summary aggregation service for daily/weekly KPI snapshots."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from typing import Final
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from godlife_backend.domain.entities import DailySummary, WeeklySummary
from godlife_backend.domain.ports import SummaryRepository, UserRepository

_DEFAULT_FALLBACK_TIMEZONE: Final[str] = "Asia/Seoul"
_WEEK_DAYS: Final[int] = 7
_MAX_STREAK_LOOKBACK_DAYS: Final[int] = 365


class SummaryService:
    def __init__(
        self,
        summary_repository: SummaryRepository,
        user_repository: UserRepository,
        fallback_timezone: str = _DEFAULT_FALLBACK_TIMEZONE,
    ) -> None:
        self._summary_repository = summary_repository
        self._user_repository = user_repository
        self._fallback_timezone = fallback_timezone

    def get_daily_summary(self, user_id: UUID, target_date: date) -> DailySummary:
        return self.recompute_daily(user_id=user_id, summary_date=target_date)

    def get_weekly_summary(self, user_id: UUID, start_date: date) -> WeeklySummary:
        return self.recompute_weekly(user_id=user_id, start_date=start_date)

    def recompute_daily(
        self,
        *,
        user_id: UUID,
        summary_date: date,
        reason: str = "manual",
    ) -> DailySummary:
        del reason
        timezone = self._resolve_timezone(user_id)
        total_sets, done_sets = self._summary_repository.aggregate_exercise_sets(
            user_id=user_id,
            summary_date=summary_date,
        )
        total_sets, done_sets = self._normalize_set_counts(total_sets, done_sets)
        completion_rate = self._completion_rate(
            total_sets=total_sets, done_sets=done_sets
        )
        reading_completed = self._has_reading_completion_on_local_date(
            user_id=user_id,
            target_date=summary_date,
            timezone=timezone,
        )

        previous_rate = self._completion_rate_for_date(
            user_id=user_id,
            target_date=summary_date - timedelta(days=1),
        )
        streak_days = self._streak_days(
            user_id=user_id,
            basis_date=summary_date,
            timezone=timezone,
        )
        summary = DailySummary(
            user_id=user_id,
            summary_date=summary_date,
            timezone=timezone,
            exercise_total_sets=total_sets,
            exercise_done_sets=done_sets,
            exercise_completion_rate=completion_rate,
            reading_completed=reading_completed,
            streak_days=streak_days,
            trend=self._trend(
                current_value=completion_rate, previous_value=previous_rate
            ),
            computed_at=datetime.now(UTC),
        )
        return self._summary_repository.upsert_daily(summary)

    def recompute_weekly(
        self,
        *,
        user_id: UUID,
        start_date: date,
        reason: str = "manual",
    ) -> WeeklySummary:
        del reason
        timezone = self._resolve_timezone(user_id)
        end_date = start_date + timedelta(days=_WEEK_DAYS - 1)

        points: list[dict[str, object]] = []
        completion_values: list[float] = []
        for day_offset in range(_WEEK_DAYS):
            target_date = start_date + timedelta(days=day_offset)
            daily_summary = self.recompute_daily(
                user_id=user_id,
                summary_date=target_date,
                reason="weekly_recompute",
            )
            completion_values.append(daily_summary.exercise_completion_rate)
            points.append(
                {
                    "date": target_date.isoformat(),
                    "exercise_completion_rate": daily_summary.exercise_completion_rate,
                    "reading_completed": daily_summary.reading_completed,
                }
            )

        week_avg = self._average(completion_values)
        previous_week_avg = self._weekly_average_for_previous_window(
            user_id=user_id,
            start_date=start_date,
        )
        weekly_summary = WeeklySummary(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            daily_points=points,
            week_avg_completion_rate=week_avg,
            streak_days=0,
            trend=self._trend(current_value=week_avg, previous_value=previous_week_avg),
            computed_at=datetime.now(UTC),
        )
        if points:
            last_daily = self._summary_repository.get_daily(user_id, end_date)
            weekly_summary.streak_days = (
                last_daily.streak_days if last_daily is not None else 0
            )
        return self._summary_repository.upsert_weekly(weekly_summary)

    def _resolve_timezone(self, user_id: UUID) -> str:
        user = self._user_repository.get_by_id(user_id)
        if user is None or not user.timezone:
            return self._fallback_timezone
        try:
            ZoneInfo(user.timezone)
            return user.timezone
        except ZoneInfoNotFoundError:
            return self._fallback_timezone

    def _completion_rate_for_date(self, user_id: UUID, target_date: date) -> float:
        total_sets, done_sets = self._summary_repository.aggregate_exercise_sets(
            user_id=user_id,
            summary_date=target_date,
        )
        total_sets, done_sets = self._normalize_set_counts(total_sets, done_sets)
        return self._completion_rate(total_sets=total_sets, done_sets=done_sets)

    def _completion_rate(self, *, total_sets: int, done_sets: int) -> float:
        if total_sets <= 0:
            return 0.0
        return round(done_sets / total_sets, 4)

    def _normalize_set_counts(self, total_sets: int, done_sets: int) -> tuple[int, int]:
        normalized_total = max(total_sets, 0)
        normalized_done = min(max(done_sets, 0), normalized_total)
        return normalized_total, normalized_done

    def _has_reading_completion_on_local_date(
        self,
        *,
        user_id: UUID,
        target_date: date,
        timezone: str,
    ) -> bool:
        tz = ZoneInfo(timezone)
        local_start = datetime.combine(target_date, time.min, tzinfo=tz)
        local_end = datetime.combine(target_date, time.max, tzinfo=tz)
        return self._summary_repository.has_reading_completion(
            user_id=user_id,
            window_start_utc=local_start.astimezone(UTC),
            window_end_utc=local_end.astimezone(UTC),
        )

    def _streak_days(self, *, user_id: UUID, basis_date: date, timezone: str) -> int:
        streak = 0
        cursor = basis_date
        for _ in range(_MAX_STREAK_LOOKBACK_DAYS):
            total_sets, done_sets = self._summary_repository.aggregate_exercise_sets(
                user_id=user_id,
                summary_date=cursor,
            )
            _, normalized_done_sets = self._normalize_set_counts(total_sets, done_sets)
            reading_completed = self._has_reading_completion_on_local_date(
                user_id=user_id,
                target_date=cursor,
                timezone=timezone,
            )
            if normalized_done_sets <= 0 and not reading_completed:
                break
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def _weekly_average_for_previous_window(
        self, *, user_id: UUID, start_date: date
    ) -> float:
        previous_values: list[float] = []
        previous_start = start_date - timedelta(days=_WEEK_DAYS)
        for day_offset in range(_WEEK_DAYS):
            target_date = previous_start + timedelta(days=day_offset)
            previous_values.append(
                self._completion_rate_for_date(user_id=user_id, target_date=target_date)
            )
        return self._average(previous_values)

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 4)

    def _trend(self, *, current_value: float, previous_value: float) -> str:
        if current_value > previous_value:
            return "up"
        if current_value < previous_value:
            return "down"
        return "flat"
