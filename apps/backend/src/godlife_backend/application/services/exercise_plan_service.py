"""Exercise plan use-case implementation for PR-03."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Final
from uuid import UUID

from godlife_backend.db.enums import PlanStatus, SetStatus
from godlife_backend.domain.entities import (
    ExercisePlan,
    ExerciseSession,
    ExerciseSetState,
)
from godlife_backend.domain.ports import (
    ExercisePlanRepository,
    ExerciseSessionRepository,
    ExerciseSetStateRepository,
    OutboxEventRepository,
)


@dataclass(slots=True)
class GeneratePlanCommand:
    user_id: UUID
    target_date: date
    source: str = "rule"


@dataclass(frozen=True, slots=True)
class _SessionSeed:
    order_no: int
    exercise_name: str
    body_part: str | None
    target_sets: int
    target_reps: int | None
    target_weight_kg: float | None
    target_rest_sec: int | None
    notes: str | None = None


class PlanConflictError(Exception):
    """Raised when ACTIVE exercise plan already exists for user/date."""


class InvalidPlanSourceError(ValueError):
    """Raised when plan source is unsupported."""


_ALLOWED_SOURCES: Final[frozenset[str]] = frozenset({"rule", "llm"})
_SESSION_SEEDS: Final[tuple[_SessionSeed, ...]] = (
    _SessionSeed(
        order_no=1,
        exercise_name="Bench Press",
        body_part="chest",
        target_sets=3,
        target_reps=10,
        target_weight_kg=30.0,
        target_rest_sec=90,
    ),
    _SessionSeed(
        order_no=2,
        exercise_name="Barbell Row",
        body_part="back",
        target_sets=3,
        target_reps=10,
        target_weight_kg=30.0,
        target_rest_sec=90,
    ),
    _SessionSeed(
        order_no=3,
        exercise_name="Plank",
        body_part="core",
        target_sets=3,
        target_reps=None,
        target_weight_kg=None,
        target_rest_sec=60,
        notes="Hold for 45 seconds per set.",
    ),
)


class ExercisePlanService:
    def __init__(
        self,
        plan_repository: ExercisePlanRepository,
        session_repository: ExerciseSessionRepository,
        set_state_repository: ExerciseSetStateRepository,
        outbox_repository: OutboxEventRepository,
    ) -> None:
        self._plan_repository = plan_repository
        self._session_repository = session_repository
        self._set_state_repository = set_state_repository
        self._outbox_repository = outbox_repository

    def generate_plan(self, command: GeneratePlanCommand) -> ExercisePlan:
        source = self._normalize_source(command.source)
        existing = self._plan_repository.get_active_by_user_and_date(
            user_id=command.user_id,
            target_date=command.target_date,
        )
        if existing is not None:
            raise PlanConflictError(
                "An ACTIVE exercise plan already exists for this user and target_date."
            )

        plan = ExercisePlan(
            user_id=command.user_id,
            target_date=command.target_date,
            source=source,
            status=PlanStatus.ACTIVE,
        )
        saved_plan = self._plan_repository.save(plan)

        for seed in _SESSION_SEEDS:
            self._validate_seed(seed)
            session = ExerciseSession(
                plan_id=saved_plan.id,
                order_no=seed.order_no,
                exercise_name=seed.exercise_name,
                body_part=seed.body_part,
                target_sets=seed.target_sets,
                target_reps=seed.target_reps,
                target_weight_kg=seed.target_weight_kg,
                target_rest_sec=seed.target_rest_sec,
                notes=seed.notes,
            )
            saved_session = self._session_repository.save(session)
            for set_no in range(1, seed.target_sets + 1):
                self._set_state_repository.save(
                    ExerciseSetState(
                        session_id=saved_session.id,
                        set_no=set_no,
                        status=SetStatus.PENDING,
                    )
                )

        return saved_plan

    def complete_active_plan(self, plan_id: UUID) -> ExercisePlan | None:
        existing = self._plan_repository.get_by_id(plan_id)
        if existing is None:
            return None
        raise NotImplementedError(
            "PR-01: Plan completion transition is not implemented yet."
        )

    @property
    def repositories(self) -> tuple:
        return (
            self._plan_repository,
            self._session_repository,
            self._set_state_repository,
            self._outbox_repository,
        )

    def _normalize_source(self, source: str) -> str:
        normalized = source.strip().lower()
        if normalized not in _ALLOWED_SOURCES:
            allowed_sources = ", ".join(sorted(_ALLOWED_SOURCES))
            raise InvalidPlanSourceError(f"source must be one of [{allowed_sources}]")
        return normalized

    def _validate_seed(self, seed: _SessionSeed) -> None:
        if seed.target_sets <= 0:
            raise ValueError("target_sets must be greater than 0")
        if seed.target_reps is not None and seed.target_reps <= 0:
            raise ValueError("target_reps must be greater than 0")
        if seed.target_weight_kg is not None and seed.target_weight_kg < 0:
            raise ValueError("target_weight_kg must be greater than or equal to 0")
        if seed.target_rest_sec is not None and seed.target_rest_sec < 0:
            raise ValueError("target_rest_sec must be greater than or equal to 0")
