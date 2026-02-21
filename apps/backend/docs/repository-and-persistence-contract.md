# 저장소 Port 및 영속성 계약

## 1. 목표
도메인 계층은 persistence를 직접 모르면 안 되며, 포트 인터페이스로만 상호작용한다.

## 2. 핵심 Port 시그니처(개념)
- `UserRepository`
  - `get_by_id(id)`, `get_by_kakao_user_id(kakao_user_id)`, `save(user)`
- `UserProfileRepository`
  - `get_by_user_id(user_id)`, `save(profile)`
- `ExercisePlanRepository`
  - `get_active_by_user_and_date(user_id, date)`, `get_by_id(plan_id)`, `list_by_user(user_id, from, to, status)`, `save(plan)`
- `ExerciseSessionRepository`
  - `list_by_plan(plan_id)`, `get_by_id(session_id)`, `save(session)`
- `ExerciseSetStateRepository`
  - `get(session_id, set_no)`, `list_pending(plan_id)`, `save(state)`
- `ReadingPlanRepository`
  - `get_by_user(user_id)`, `save(plan)`
- `ReadingLogRepository`
  - `list(user_id, from, to)`, `get_by_id(log_id)`, `save(log)`
- `NotificationRepository`
  - `get_by_id(id)`, `get_by_idempotency_key(key)`, `save(notification)`, `list(user_id, status, from, to)`
- `WebhookEventRepository`
  - `get_by_provider_and_key(provider, key)`, `save(event)`
  - `get_by_provider_and_event_id(provider, event_id)`, `mark_failed(event_id, reason)`
- `OutboxEventRepository`
  - `lease_pending(limit)`, `save(event)`, `mark_complete(event_id)`, `mark_failed(event_id, reason)`

## 3. 영속성 규칙
- 조회 정렬은 deterministic (`created_at desc` 기본)
- write는 optimistic concurrency 고려
- 동일 키 제약 충돌은 domain 충돌로 치환
- `WebhookEventRepository`는 `(provider, idempotency_key)`와 `(provider, event_id)` 유니크 정책을 모두 지원해야 한다.
- `NotificationRepository`는 `idempotency_key`를 기준으로 no-op 흐름을 제공하고 `manual_review` 진입 사유를 저장 가능해야 한다.

## 4. 동시성
- 세트 상태 갱신은 transaction + lock 범위를 최소화
- 웹훅 병행 수신은 idempotency 검사 선행 후 no-op
- 대기 중 알림 처리는 `lease_pending(limit)`에서 `(status='PENDING' OR status='RETRY_SCHEDULED')` 필터로 조회하고 `updated_at` 오름차순 정렬을 보장한다.
