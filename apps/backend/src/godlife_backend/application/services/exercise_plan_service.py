"""Exercise plan use-case skeleton for PR-01."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from godlife_backend.domain.entities import ExercisePlan
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
        raise NotImplementedError(
            "PR-01: Exercise plan generation use case is not implemented yet."
        )

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
