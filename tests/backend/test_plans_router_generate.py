from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from godlife_backend.adapter.test_doubles import (
    InMemoryExercisePlanRepository,
    InMemoryExerciseSessionRepository,
    InMemoryExerciseSetStateRepository,
)
from godlife_backend.adapter.webapi.routers.plans import (
    GeneratePlanRequest,
    PlanResponse,
    generate_plan,
)
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
)
from godlife_backend.db.enums import OutboxStatus
from godlife_backend.domain.entities import OutboxEvent
from godlife_backend.domain.ports import OutboxEventRepository


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
        self._events[event.id] = event
        return event

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        event = self._events.get(event_id)
        if event is None:
            return None
        event.status = OutboxStatus.FAILED
        event.payload["reason"] = reason
        self._events[event.id] = event
        return event


@pytest.fixture()
def service() -> ExercisePlanService:
    return ExercisePlanService(
        plan_repository=InMemoryExercisePlanRepository(),
        session_repository=InMemoryExerciseSessionRepository(),
        set_state_repository=InMemoryExerciseSetStateRepository(),
        outbox_repository=_InMemoryOutboxEventRepository(),
    )


def test_generate_plan_with_plan_source_returns_active(
    service: ExercisePlanService,
) -> None:
    request = GeneratePlanRequest(
        user_id=uuid4(),
        target_date=date(2026, 2, 22),
        plan_source="llm",
    )

    response = generate_plan(request=request, service=service)

    assert isinstance(response, PlanResponse)
    assert response.source == "llm"
    assert response.status == "ACTIVE"


def test_generate_plan_with_source_field_returns_active(
    service: ExercisePlanService,
) -> None:
    request = GeneratePlanRequest(
        user_id=uuid4(),
        target_date=date(2026, 2, 23),
        source="rule",
    )

    response = generate_plan(request=request, service=service)

    assert isinstance(response, PlanResponse)
    assert response.source == "rule"
    assert response.status == "ACTIVE"


def test_generate_plan_duplicate_request_returns_conflict(
    service: ExercisePlanService,
) -> None:
    user_id = uuid4()
    target_date = date(2026, 2, 24)
    first_request = GeneratePlanRequest(
        user_id=user_id,
        target_date=target_date,
        plan_source="llm",
    )
    second_request = GeneratePlanRequest(
        user_id=user_id,
        target_date=target_date,
        plan_source="llm",
    )

    first_response = generate_plan(request=first_request, service=service)
    assert first_response.status == "ACTIVE"

    with pytest.raises(HTTPException) as exc_info:
        generate_plan(request=second_request, service=service)

    assert exc_info.value.status_code == 409


def test_generate_plan_invalid_source_returns_400(
    service: ExercisePlanService,
) -> None:
    request = GeneratePlanRequest(
        user_id=uuid4(),
        target_date=date(2026, 2, 25),
        source="bad",
    )

    with pytest.raises(HTTPException) as exc_info:
        generate_plan(request=request, service=service)

    assert exc_info.value.status_code == 400
