from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from uuid import UUID, uuid4

import pytest
from godlife_backend.adapter.test_doubles import (
    InMemoryExercisePlanRepository,
    InMemoryExerciseSessionRepository,
    InMemoryExerciseSetStateRepository,
    InMemoryNotificationRepository,
    InMemoryOutboxEventRepository,
    InMemoryReadingLogRepository,
    InMemoryUserProfileRepository,
    InMemoryUserRepository,
    InMemoryWebhookEventRepository,
)
from godlife_backend.application.services.exercise_plan_service import (
    ExercisePlanService,
    GeneratePlanCommand,
)
from godlife_backend.application.services.notification_service import (
    NotificationService,
)
from godlife_backend.application.services.webhook_service import WebhookService
from godlife_backend.db.enums import (
    NotificationStatus,
    OutboxStatus,
    PlanStatus,
    SetStatus,
)
from godlife_backend.domain.entities import (
    ExercisePlan,
    ExerciseSession,
    ExerciseSetState,
    Notification,
    OutboxEvent,
    ReadingLog,
    User,
    UserProfile,
    WebhookEvent,
)


class _OutboxStub:
    def lease_pending(self, limit: int = 100) -> list[OutboxEvent]:
        return []

    def save(self, event: OutboxEvent) -> OutboxEvent:
        return event

    def mark_complete(self, event_id: UUID) -> OutboxEvent | None:
        return None

    def mark_failed(self, event_id: UUID, reason: str | None) -> OutboxEvent | None:
        return None


def test_in_memory_user_repository_can_find_by_kakao_user_id() -> None:
    repository = InMemoryUserRepository()
    user = User(id=uuid4(), kakao_user_id="kakao-1")

    repository.save(user)

    assert repository.get_by_id(user.id) == user
    assert repository.get_by_kakao_user_id("kakao-1") == user
    assert repository.get_by_kakao_user_id("missing") is None


def test_in_memory_user_profile_repository_filters_by_user_id() -> None:
    repository = InMemoryUserProfileRepository()
    user_id = uuid4()
    repository.save(UserProfile(id=uuid4(), user_id=user_id, goal="근력"))
    repository.save(
        UserProfile(
            id=uuid4(),
            user_id=uuid4(),
            goal="체력",
        )
    )

    profile = repository.get_by_user_id(user_id)
    assert profile is not None
    assert profile.goal == "근력"


def test_in_memory_exercise_plan_repository_filters_and_sorts() -> None:
    repository = InMemoryExercisePlanRepository()
    user_id = uuid4()
    old_date = date(2026, 1, 1)
    new_date = date(2026, 1, 3)
    earlier = datetime(2026, 1, 1, 9, 0)
    later = datetime(2026, 1, 3, 9, 0)

    repository.save(
        ExercisePlan(
            id=uuid4(),
            user_id=user_id,
            target_date=old_date,
            status=PlanStatus.ACTIVE,
            created_at=later,
        )
    )
    repository.save(
        ExercisePlan(
            id=uuid4(),
            user_id=user_id,
            target_date=new_date,
            status=PlanStatus.DRAFT,
            created_at=earlier,
        )
    )

    plans = repository.list_by_user(user_id=user_id, status=PlanStatus.ACTIVE)
    assert len(plans) == 1
    assert plans[0].target_date == old_date

    plans = repository.list_by_user(
        user_id=user_id,
        from_date=old_date,
        to_date=old_date,
    )
    assert len(plans) == 1

    plans = repository.list_by_user(user_id=user_id)
    assert plans[0].created_at >= plans[1].created_at


def test_in_memory_exercise_plan_repository_get_active_by_user_and_date() -> None:
    repository = InMemoryExercisePlanRepository()
    user_id = uuid4()
    target_date = date(2026, 1, 1)

    repository.save(
        ExercisePlan(
            id=uuid4(),
            user_id=user_id,
            target_date=target_date,
            status=PlanStatus.DRAFT,
        )
    )
    active = ExercisePlan(
        id=uuid4(),
        user_id=user_id,
        target_date=target_date,
        status=PlanStatus.ACTIVE,
    )
    repository.save(active)

    assert repository.get_active_by_user_and_date(user_id, target_date) == active


def test_in_memory_exercise_session_repository_orders_by_order_no() -> None:
    repository = InMemoryExerciseSessionRepository()
    plan_id = uuid4()
    repository.save(
        ExerciseSession(id=uuid4(), plan_id=plan_id, order_no=2, exercise_name="스쿼트")
    )
    repository.save(
        ExerciseSession(id=uuid4(), plan_id=plan_id, order_no=1, exercise_name="벤치")
    )

    sessions = repository.list_by_plan(plan_id)
    assert [session.order_no for session in sessions] == [1, 2]


def test_in_memory_exercise_set_state_repository_list_pending_by_session_only() -> None:
    repository = InMemoryExerciseSetStateRepository()
    session_id = uuid4()
    other_session_id = uuid4()
    repository.save(
        ExerciseSetState(
            id=uuid4(),
            session_id=session_id,
            set_no=2,
            status=SetStatus.DONE,
        )
    )
    repository.save(
        ExerciseSetState(
            id=uuid4(),
            session_id=session_id,
            set_no=1,
            status=SetStatus.PENDING,
        )
    )
    repository.save(
        ExerciseSetState(
            id=uuid4(),
            session_id=other_session_id,
            set_no=0,
            status=SetStatus.PENDING,
        )
    )

    pending = repository.list_pending(session_id)
    assert [state.set_no for state in pending] == [1]


def test_in_memory_reading_log_repository_filters_by_date_range() -> None:
    repository = InMemoryReadingLogRepository()
    user_id = uuid4()
    repository.save(
        ReadingLog(
            id=uuid4(),
            user_id=user_id,
            created_at=datetime(2026, 1, 1, 10, 0),
        )
    )
    repository.save(
        ReadingLog(
            id=uuid4(),
            user_id=user_id,
            created_at=datetime(2026, 1, 3, 10, 0),
        )
    )
    repository.save(
        ReadingLog(
            id=uuid4(),
            user_id=user_id,
            created_at=datetime(2026, 1, 2, 10, 0),
        )
    )

    logs = repository.list(
        user_id=user_id,
        from_date=date(2026, 1, 2),
        to_date=date(2026, 1, 3),
    )
    assert [log.created_at.day for log in logs] == [3, 2]


def test_in_memory_notification_repository_filters_status_and_date() -> None:
    repository = InMemoryNotificationRepository()
    user_id = uuid4()
    repository.save(
        Notification(
            id=uuid4(),
            user_id=user_id,
            status=NotificationStatus.SCHEDULED,
            schedule_at=datetime(2026, 1, 1, 9, 0),
        )
    )
    repository.save(
        Notification(
            id=uuid4(),
            user_id=user_id,
            status=NotificationStatus.SENT,
            schedule_at=datetime(2026, 1, 2, 9, 0),
            idempotency_key="send-1",
        )
    )

    notifications = repository.list(
        user_id=user_id,
        status=NotificationStatus.SENT,
        to_at=date(2026, 1, 2),
    )
    assert len(notifications) == 1
    assert notifications[0].idempotency_key == "send-1"

    assert repository.get_by_idempotency_key("send-1") is not None


def test_in_memory_webhook_event_repository_sets_failure_reason() -> None:
    repository = InMemoryWebhookEventRepository()
    repository.save(
        event := WebhookEvent(
            id=uuid4(),
            provider="stripe",
            event_id="evt-1",
            idempotency_key="idemp",
        )
    )
    repository.mark_failed(event.id, "invalid_payload")

    assert repository.get_by_provider_and_event_id("stripe", "evt-1") == event
    assert repository.get_by_provider_and_key("stripe", "idemp") == event
    assert event.reason_code == "invalid_payload"


def test_in_memory_outbox_repository_lease_only_pending_and_limit() -> None:
    repository = InMemoryOutboxEventRepository()
    repository.save(
        OutboxEvent(
            id=uuid4(),
            aggregate_type="plan",
            aggregate_id=uuid4(),
            event_type="completed",
            status=OutboxStatus.PENDING,
            created_at=datetime(2026, 1, 2, 10, 0),
        )
    )
    repository.save(
        OutboxEvent(
            id=uuid4(),
            aggregate_type="plan",
            aggregate_id=uuid4(),
            event_type="started",
            status=OutboxStatus.IN_FLIGHT,
            created_at=datetime(2026, 1, 1, 9, 0),
        )
    )
    repository.save(
        OutboxEvent(
            id=uuid4(),
            aggregate_type="plan",
            aggregate_id=uuid4(),
            event_type="failed",
            status=OutboxStatus.PENDING,
            created_at=datetime(2026, 1, 3, 11, 0),
        )
    )

    assert [event.event_type for event in repository.lease_pending(limit=1)] == [
        "completed"
    ]
    events = repository.lease_pending(limit=10)
    assert len(events) == 2
    assert [event.event_type for event in events] == ["completed", "failed"]

    mark = repository.mark_complete(events[0].id)
    assert mark is not None
    assert mark.status == OutboxStatus.COMPLETED


def test_in_memory_outbox_mark_failed_adds_payload_reason() -> None:
    repository = InMemoryOutboxEventRepository()
    event = OutboxEvent(
        id=uuid4(),
        aggregate_type="plan",
        aggregate_id=uuid4(),
        event_type="completed",
        status=OutboxStatus.PENDING,
        payload={"k": "v"},
    )
    repository.save(event)
    repository.mark_failed(event.id, "error")

    assert event.status == OutboxStatus.FAILED
    assert event.payload["failure_reason"] == "error"


class _PlanServiceRepo:
    def __init__(self, plan: ExercisePlan | None = None) -> None:
        self.plan = plan

    def get_by_id(self, plan_id: UUID) -> ExercisePlan | None:
        return self.plan

    def get_active_by_user_and_date(
        self, user_id: UUID, target_date: date
    ) -> ExercisePlan | None:
        return None

    def list_by_user(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        status: PlanStatus | None = None,
    ) -> list[ExercisePlan]:
        del user_id, from_date, to_date, status
        return []

    def save(self, plan: ExercisePlan) -> ExercisePlan:
        return plan


def test_exercise_plan_service_complete_active_plan_returns_none_when_missing() -> None:
    service = ExercisePlanService(
        plan_repository=_PlanServiceRepo(),
        session_repository=InMemoryExerciseSessionRepository(),
        set_state_repository=InMemoryExerciseSetStateRepository(),
        outbox_repository=_OutboxStub(),
    )

    assert service.complete_active_plan(uuid4()) is None


def test_exercise_plan_service_generate_plan_creates_plan_sessions_and_sets() -> None:
    session_repository = InMemoryExerciseSessionRepository()
    set_state_repository = InMemoryExerciseSetStateRepository()
    service = ExercisePlanService(
        plan_repository=_PlanServiceRepo(),
        session_repository=session_repository,
        set_state_repository=set_state_repository,
        outbox_repository=_OutboxStub(),
    )

    plan = service.generate_plan(
        GeneratePlanCommand(
            user_id=uuid4(),
            target_date=date(2026, 1, 1),
        )
    )

    assert plan.status == PlanStatus.ACTIVE
    assert plan.source == "rule"
    sessions = session_repository.list_by_plan(plan.id)
    assert sessions
    for session in sessions:
        assert len(set_state_repository.list_pending(session.id)) == session.target_sets


def test_exercise_plan_service_complete_active_plan_not_implemented_when_exists() -> (
    None
):
    service = ExercisePlanService(
        plan_repository=_PlanServiceRepo(ExercisePlan(id=uuid4())),
        session_repository=InMemoryExerciseSessionRepository(),
        set_state_repository=InMemoryExerciseSetStateRepository(),
        outbox_repository=_OutboxStub(),
    )

    with pytest.raises(NotImplementedError):
        service.complete_active_plan(uuid4())


class _NotificationRepo:
    def __init__(self, notification: Notification | None = None) -> None:
        self.notification = notification

    def get_by_id(self, notification_id: UUID) -> Notification | None:
        return self.notification

    def get_by_idempotency_key(self, idempotency_key: str) -> Notification | None:
        return None

    def list(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        from_at: date | None = None,
        to_at: date | None = None,
    ) -> Sequence[Notification]:
        del user_id, status, from_at, to_at
        return []

    def save(self, notification: Notification) -> Notification:
        return notification


def test_notification_service_create_pending_notification_creates_scheduled() -> None:
    service = NotificationService(
        notification_repository=_NotificationRepo(),
        outbox_repository=_OutboxStub(),
    )
    notification = service.create_pending_notification(
        user_id=uuid4(),
        kind="reminder",
        related_id=None,
        schedule_at=datetime(2026, 1, 1, 9, 0),
    )
    assert notification.status == NotificationStatus.SCHEDULED
    assert notification.kind == "reminder"


def test_notification_service_mark_as_retried_not_found_and_updates_status() -> None:
    service = NotificationService(
        notification_repository=_NotificationRepo(),
        outbox_repository=_OutboxStub(),
    )
    assert service.mark_as_retried(uuid4()) is None

    service = NotificationService(
        notification_repository=_NotificationRepo(Notification(id=uuid4())),
        outbox_repository=_OutboxStub(),
    )
    retried = service.mark_as_retried(uuid4())
    assert retried is not None
    assert retried.status == NotificationStatus.RETRY_SCHEDULED
    assert retried.retry_count == 1


def test_webhook_service_handle_event_and_replay_behavior() -> None:
    service = WebhookService(
        webhook_event_repository=InMemoryWebhookEventRepository(),
        outbox_repository=_OutboxStub(),
    )
    first = service.handle_event(
        WebhookEvent(
            provider="stripe",
            event_type="payment",
            event_id="evt-1",
            idempotency_key="stripe:payment:evt-1",
        )
    )
    second = service.handle_event(
        WebhookEvent(
            provider="stripe",
            event_type="payment",
            event_id="evt-1",
            idempotency_key="stripe:payment:evt-1",
        )
    )
    assert second.id == first.id

    assert service.replay_failed_events(provider="stripe", limit=10) == []
