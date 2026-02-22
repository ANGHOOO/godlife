from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

import pytest
from godlife_backend.adapter.test_doubles import (
    InMemoryExercisePlanRepository,
    InMemoryExerciseSessionRepository,
    InMemoryExerciseSetStateRepository,
    InMemoryNotificationRepository,
)
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
    GeneratePlanCommand,
    InvalidPlanSourceError,
    PlanConflictError,
    SetOrderViolationError,
    SetResultCommand,
)
from godlife_backend.db.enums import OutboxStatus, PlanStatus, SetStatus
from godlife_backend.domain.entities import ExercisePlan, OutboxEvent
from godlife_backend.domain.ports import OutboxEventRepository
from sqlalchemy.exc import IntegrityError


class _InMemoryOutboxEventRepository(OutboxEventRepository):
    def __init__(self) -> None:
        self._events: dict[UUID, OutboxEvent] = {}

    def lease_pending(self, limit: int = 100) -> list[OutboxEvent]:
        pending = [
            event
            for event in self._events.values()
            if event.status == OutboxStatus.PENDING
        ]
        return pending[:limit]

    def save(self, event: OutboxEvent) -> OutboxEvent:
        self._events[event.id] = event
        return event

    def mark_complete(self, event_id: UUID) -> OutboxEvent | None:
        event = self._events.get(event_id)
        if event is None:
            return None
        event.status = OutboxStatus.COMPLETED
        self._events[event_id] = event
        return event

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        event = self._events.get(event_id)
        if event is None:
            return None
        event.status = OutboxStatus.FAILED
        event.payload["reason"] = reason
        self._events[event_id] = event
        return event


@pytest.fixture()
def service_bundle() -> tuple[
    ExercisePlanService,
    InMemoryExercisePlanRepository,
    InMemoryExerciseSessionRepository,
    InMemoryExerciseSetStateRepository,
]:
    plan_repository = InMemoryExercisePlanRepository()
    session_repository = InMemoryExerciseSessionRepository()
    set_state_repository = InMemoryExerciseSetStateRepository()
    service = ExercisePlanService(
        plan_repository=plan_repository,
        session_repository=session_repository,
        set_state_repository=set_state_repository,
        outbox_repository=_InMemoryOutboxEventRepository(),
    )
    return service, plan_repository, session_repository, set_state_repository


def test_generate_plan_creates_sessions_and_pending_sets(
    service_bundle: tuple[
        ExercisePlanService,
        InMemoryExercisePlanRepository,
        InMemoryExerciseSessionRepository,
        InMemoryExerciseSetStateRepository,
    ],
) -> None:
    service, _, session_repository, set_state_repository = service_bundle
    command = GeneratePlanCommand(
        user_id=uuid4(),
        target_date=date(2026, 2, 22),
        source="llm",
    )

    plan = service.generate_plan(command)

    assert plan.status == PlanStatus.ACTIVE
    assert plan.source == "llm"
    sessions = session_repository.list_by_plan(plan.id)
    assert len(sessions) == 3

    total_target_sets = sum(session.target_sets for session in sessions)
    total_pending_sets = sum(
        len(set_state_repository.list_pending(session.id)) for session in sessions
    )
    assert total_pending_sets == total_target_sets

    for session in sessions:
        pending = set_state_repository.list_pending(session.id)
        assert [state.set_no for state in pending] == list(
            range(1, session.target_sets + 1)
        )
        assert all(state.status == SetStatus.PENDING for state in pending)


def test_generate_plan_raises_conflict_for_same_user_and_date(
    service_bundle: tuple[
        ExercisePlanService,
        InMemoryExercisePlanRepository,
        InMemoryExerciseSessionRepository,
        InMemoryExerciseSetStateRepository,
    ],
) -> None:
    service, _, _, _ = service_bundle
    user_id = uuid4()
    target_date = date(2026, 2, 22)

    service.generate_plan(
        GeneratePlanCommand(user_id=user_id, target_date=target_date, source="rule")
    )

    with pytest.raises(PlanConflictError):
        service.generate_plan(
            GeneratePlanCommand(user_id=user_id, target_date=target_date, source="rule")
        )


def test_generate_plan_rejects_invalid_source(
    service_bundle: tuple[
        ExercisePlanService,
        InMemoryExercisePlanRepository,
        InMemoryExerciseSessionRepository,
        InMemoryExerciseSetStateRepository,
    ],
) -> None:
    service, _, _, _ = service_bundle

    with pytest.raises(InvalidPlanSourceError):
        service.generate_plan(
            GeneratePlanCommand(
                user_id=uuid4(),
                target_date=date(2026, 2, 22),
                source="invalid-source",
            )
        )


class _IntegrityErrorPlanRepository(InMemoryExercisePlanRepository):
    def __init__(self, db_error: Exception) -> None:
        super().__init__()
        self._db_error = db_error

    def save(self, plan: ExercisePlan) -> ExercisePlan:
        del plan
        raise IntegrityError("insert", {}, self._db_error)


class _FakeDiag:
    def __init__(self, constraint_name: str | None) -> None:
        self.constraint_name = constraint_name


class _FakeDbError(Exception):
    def __init__(
        self,
        message: str,
        *,
        sqlstate: str | None = None,
        constraint_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.sqlstate = sqlstate
        self.pgcode = sqlstate
        self.diag = _FakeDiag(constraint_name)


def test_generate_plan_maps_integrity_error_to_conflict() -> None:
    db_error = _FakeDbError(
        "duplicate key value violates unique constraint",
        sqlstate="23505",
        constraint_name="uq_exercise_plans_user_target_date_active",
    )
    service = ExercisePlanService(
        plan_repository=_IntegrityErrorPlanRepository(db_error),
        session_repository=InMemoryExerciseSessionRepository(),
        set_state_repository=InMemoryExerciseSetStateRepository(),
        outbox_repository=_InMemoryOutboxEventRepository(),
    )

    with pytest.raises(PlanConflictError):
        service.generate_plan(
            GeneratePlanCommand(
                user_id=uuid4(),
                target_date=date(2026, 2, 22),
                source="rule",
            )
        )


def test_generate_plan_does_not_map_non_conflict_integrity_error() -> None:
    db_error = _FakeDbError(
        "insert or update on table violates foreign key constraint",
        sqlstate="23503",
        constraint_name="fk_exercise_plans_user_id",
    )
    service = ExercisePlanService(
        plan_repository=_IntegrityErrorPlanRepository(db_error),
        session_repository=InMemoryExerciseSessionRepository(),
        set_state_repository=InMemoryExerciseSetStateRepository(),
        outbox_repository=_InMemoryOutboxEventRepository(),
    )

    with pytest.raises(IntegrityError):
        service.generate_plan(
            GeneratePlanCommand(
                user_id=uuid4(),
                target_date=date(2026, 2, 22),
                source="rule",
            )
        )


def test_submit_set_result_done_schedules_next_notification() -> None:
    notification_repository = InMemoryNotificationRepository()
    plan_repository = InMemoryExercisePlanRepository()
    session_repository = InMemoryExerciseSessionRepository()
    set_state_repository = InMemoryExerciseSetStateRepository()
    service = ExercisePlanService(
        plan_repository=plan_repository,
        session_repository=session_repository,
        set_state_repository=set_state_repository,
        outbox_repository=_InMemoryOutboxEventRepository(),
        notification_repository=notification_repository,
    )
    plan = service.generate_plan(
        GeneratePlanCommand(
            user_id=uuid4(),
            target_date=date(2026, 2, 22),
            source="rule",
        )
    )
    session = session_repository.list_by_plan(plan.id)[0]

    outcome = service.submit_set_result(
        SetResultCommand(
            plan_id=plan.id,
            session_id=session.id,
            set_no=1,
            result="DONE",
            performed_reps=10,
        )
    )

    assert outcome.state.status == SetStatus.DONE
    assert outcome.next_pending_set_no == 2
    assert outcome.notification_id is not None


def test_submit_set_result_blocks_out_of_order_completion() -> None:
    plan_repository = InMemoryExercisePlanRepository()
    session_repository = InMemoryExerciseSessionRepository()
    set_state_repository = InMemoryExerciseSetStateRepository()
    service = ExercisePlanService(
        plan_repository=plan_repository,
        session_repository=session_repository,
        set_state_repository=set_state_repository,
        outbox_repository=_InMemoryOutboxEventRepository(),
    )
    plan = service.generate_plan(
        GeneratePlanCommand(
            user_id=uuid4(),
            target_date=date(2026, 2, 22),
            source="rule",
        )
    )
    session = session_repository.list_by_plan(plan.id)[0]

    with pytest.raises(SetOrderViolationError):
        service.submit_set_result(
            SetResultCommand(
                plan_id=plan.id,
                session_id=session.id,
                set_no=2,
                result="DONE",
            )
        )
