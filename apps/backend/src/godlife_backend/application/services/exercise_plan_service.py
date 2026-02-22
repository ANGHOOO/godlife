"""Exercise plan use-case implementation for PR-03."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Final
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from godlife_backend.db.enums import PlanStatus, SetStatus
from godlife_backend.domain.entities import (
    ExercisePlan,
    ExerciseSession,
    ExerciseSetState,
    Notification,
)
from godlife_backend.domain.ports import (
    ExercisePlanRepository,
    ExerciseSessionRepository,
    ExerciseSetStateRepository,
    NotificationRepository,
    OutboxEventRepository,
)


@dataclass(slots=True)
class GeneratePlanCommand:
    user_id: UUID
    target_date: date
    source: str = "rule"


@dataclass(slots=True)
class SetResultCommand:
    plan_id: UUID
    session_id: UUID
    set_no: int
    result: str
    performed_reps: int | None = None
    performed_weight_kg: float | None = None
    actual_rest_sec: int | None = None
    request_timestamp: datetime | None = None


@dataclass(slots=True)
class SetResultOutcome:
    state: ExerciseSetState
    next_pending_set_no: int | None
    notification_id: UUID | None


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


class SetResultValidationError(ValueError):
    """Raised when set result input cannot be processed."""


class SetOrderViolationError(ValueError):
    """Raised when set completion order is violated."""


class SetContextMismatchError(ValueError):
    """Raised when plan/session context is inconsistent."""


_ALLOWED_SOURCES: Final[frozenset[str]] = frozenset({"rule", "llm"})
_ACTIVE_PLAN_UNIQUE_CONSTRAINT: Final[str] = "uq_exercise_plans_user_target_date_active"
_SET_RESULT_ALLOWED_VALUES: Final[frozenset[str]] = frozenset({"DONE", "SKIPPED"})
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
        notification_repository: NotificationRepository | None = None,
    ) -> None:
        self._plan_repository = plan_repository
        self._session_repository = session_repository
        self._set_state_repository = set_state_repository
        self._outbox_repository = outbox_repository
        self._notification_repository = notification_repository

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
        try:
            saved_plan = self._plan_repository.save(plan)
        except IntegrityError as exc:
            if self._is_active_plan_conflict_integrity_error(exc):
                raise PlanConflictError(
                    "An ACTIVE exercise plan already exists "
                    "for this user and target_date."
                ) from exc
            raise

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

        self._schedule_initial_set_notification(saved_plan.id)
        return saved_plan

    def submit_set_result(self, command: SetResultCommand) -> SetResultOutcome:
        session = self._session_repository.get_by_id(command.session_id)
        if session is None:
            raise SetResultValidationError("session not found")
        if session.plan_id != command.plan_id:
            raise SetContextMismatchError("session does not belong to plan")
        if command.set_no <= 0:
            raise SetResultValidationError("set_no must be greater than 0")

        state = self._set_state_repository.get(command.session_id, command.set_no)
        if state is None:
            raise SetResultValidationError("set state not found")

        normalized_result = command.result.strip().upper()
        if normalized_result not in _SET_RESULT_ALLOWED_VALUES:
            raise SetResultValidationError("result must be DONE or SKIPPED")

        if state.status in {SetStatus.DONE, SetStatus.SKIPPED}:
            return SetResultOutcome(
                state=state,
                next_pending_set_no=None,
                notification_id=None,
            )

        if not self._can_complete_set(command.session_id, command.set_no):
            raise SetOrderViolationError("previous set must be completed first")

        occurred_at = command.request_timestamp or datetime.now(UTC)
        state.updated_at = occurred_at
        if normalized_result == "DONE":
            state.status = SetStatus.DONE
            state.performed_reps = command.performed_reps
            state.performed_weight_kg = command.performed_weight_kg
            state.actual_rest_sec = command.actual_rest_sec
            state.completed_at = occurred_at
            state.skipped_at = None
        else:
            state.status = SetStatus.SKIPPED
            state.skipped_at = occurred_at
            state.completed_at = None

        saved_state = self._set_state_repository.save(state)
        next_pending_set_no: int | None = None
        notification_id: UUID | None = None
        if normalized_result == "DONE":
            pending = [
                pending_state
                for pending_state in self._set_state_repository.list_pending(
                    command.session_id
                )
                if pending_state.set_no > command.set_no
            ]
            if pending:
                next_set = min(pending, key=lambda pending_state: pending_state.set_no)
                next_pending_set_no = next_set.set_no
                plan = self._plan_repository.get_by_id(command.plan_id)
                if plan is not None:
                    notification = self._schedule_exercise_notification(
                        user_id=plan.user_id,
                        kind="EXERCISE_NEXT_SET",
                        related_id=command.session_id,
                        idempotency_key=(
                            f"exercise:next:{command.plan_id}:{command.session_id}:"
                            f"set:{next_set.set_no}"
                        ),
                        payload={
                            "plan_id": str(command.plan_id),
                            "session_id": str(command.session_id),
                            "set_no": next_set.set_no,
                        },
                    )
                    notification_id = (
                        notification.id if notification is not None else None
                    )

        return SetResultOutcome(
            state=saved_state,
            next_pending_set_no=next_pending_set_no,
            notification_id=notification_id,
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

    def _is_active_plan_conflict_integrity_error(self, exc: IntegrityError) -> bool:
        db_error = exc.orig
        error_message = str(db_error)
        sqlstate = getattr(db_error, "sqlstate", None) or getattr(
            db_error, "pgcode", None
        )
        if sqlstate == "23505":
            diag = getattr(db_error, "diag", None)
            constraint_name = getattr(diag, "constraint_name", None)
            if constraint_name == _ACTIVE_PLAN_UNIQUE_CONSTRAINT:
                return True
            if _ACTIVE_PLAN_UNIQUE_CONSTRAINT in error_message:
                return True
        return (
            "UNIQUE constraint failed" in error_message
            and "exercise_plans.user_id" in error_message
            and "exercise_plans.target_date" in error_message
        )

    def _schedule_initial_set_notification(self, plan_id: UUID) -> None:
        sessions = self._session_repository.list_by_plan(plan_id)
        if not sessions:
            return
        first_session = sessions[0]
        first_set = self._set_state_repository.get(first_session.id, 1)
        if first_set is None or first_set.status != SetStatus.PENDING:
            return
        plan = self._plan_repository.get_by_id(plan_id)
        if plan is None:
            return
        self._schedule_exercise_notification(
            user_id=plan.user_id,
            kind="EXERCISE_START",
            related_id=first_session.id,
            idempotency_key=f"exercise:start:{plan_id}:{first_session.id}:set:1",
            payload={
                "plan_id": str(plan_id),
                "session_id": str(first_session.id),
                "set_no": 1,
            },
        )

    def _schedule_exercise_notification(
        self,
        *,
        user_id: UUID,
        kind: str,
        related_id: UUID,
        idempotency_key: str,
        payload: dict[str, object],
    ) -> Notification | None:
        if self._notification_repository is None:
            return None
        existing = self._notification_repository.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return existing
        notification = Notification(
            user_id=user_id,
            kind=kind,
            related_id=related_id,
            schedule_at=datetime.now(UTC),
            idempotency_key=idempotency_key,
            payload=payload,
        )
        return self._notification_repository.save(notification)

    def _can_complete_set(self, session_id: UUID, set_no: int) -> bool:
        for previous_set_no in range(1, set_no):
            previous = self._set_state_repository.get(session_id, previous_set_no)
            if previous is None:
                return False
            if previous.status not in {SetStatus.DONE, SetStatus.SKIPPED}:
                return False
        return True
