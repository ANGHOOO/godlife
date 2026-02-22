# Persistence Schema Contract (GOD-33)

## 목적
`persistence schema 정비 및 마이그레이션`의 실행 기준을 문서화한다.

## 영속성 모델 맵핑

### users
- `id`: `UUID` PK
- `kakao_user_id`: `STRING(255)` UNIQUE, 운영 식별자
- `name`: `STRING(120)` NOT NULL
- `timezone`: `STRING(80)` 기본값 `Asia/Seoul`
- `status`: `USERSTATUS` (`ACTIVE`, `INACTIVE`, `SUSPENDED`)
- audit: `created_at`, `updated_at`

### user_profiles
- `user_id`: FK(users.id), UNIQUE
- 키: `age`, `height_cm`, `weight_kg`, `goal`, `experience_level`, `max_daily_minutes`, `available_equipment`, `injury_notes`
- `height_cm`, `weight_kg`는 `Float`(소수점 허용)
- 규칙: `user_id` 1:1

### exercise_plans
- `user_id`: FK(users.id)
- `target_date`, `source`, `status` (`DRAFT`, `ACTIVE`, `DONE`, `CANCELED`), `summary`
- 인덱스/제약
  - `(target_date, status)` 인덱스
  - `(user_id, target_date)` 인덱스
  - PostgreSQL: `status='ACTIVE'`일 때 `user_id + target_date` 유니크
  - 부분 유니크 인덱스 이름: `uq_exercise_plans_user_target_date_active`

### exercise_sessions
- `plan_id`: FK(exercise_plans.id)
- 순서/타겟 데이터: `order_no`, `exercise_name`, `target_sets`, `target_reps`, `target_weight_kg`, `target_rest_sec`

### exercise_set_states
- `session_id`: FK(exercise_sessions.id)
- `set_no`, `status` (`PENDING`, `IN_PROGRESS`, `DONE`, `SKIPPED`, `FAILED`), `performed_reps`, `performed_weight_kg`, `actual_rest_sec`
- 유니크: `(session_id, set_no)`
- 인덱스: `(session_id)`, `(status)`

### reading_plans
- `user_id`: FK(users.id)
- `remind_time`, `goal_minutes`, `enabled`

### reading_logs
- `user_id`: FK(users.id), `reading_plan_id`, `start_at`, `end_at`, `pages_read`, `status` (`DONE`, `SKIPPED`, `ABANDONED`)
- 인덱스: `(user_id, created_at)`

### notifications
- `user_id`: FK(users.id), `kind`, `related_id`, `status`
  - 상태: `SCHEDULED`, `SENT`, `ACKNOWLEDGED`, `COMPLETE`, `FAILED`, `RETRY_SCHEDULED`, `MANUAL_REVIEW`
- `schedule_at`, `sent_at`, `retry_count`, `idempotency_key` UNIQUE
- payload 저장: `payload` (`JSONB`)
- 운영 보강 필드
  - `reason_code`
  - `provider_response_code`
  - `failure_reason`
  - `last_error_at`
  - `memo`
  - `reviewed_by`, `reviewed_at`
- 인덱스: `(user_id, status, schedule_at)`

### webhook_events
- `provider`, `event_type`, `user_id`, `idempotency_key`, `event_id`, `raw_payload`, `processed`
- 유니크:
  - `(provider, idempotency_key)`
  - `(provider, event_id)`
- webhook 운영 확장:
- `schema_version`, `request_id`, `signature_state`, `reason_code`, `retry_count`
- 인덱스: `(provider, schema_version)`, `(signature_state)`
- 인덱스: `(processed, created_at)`

### outbox_events
- `aggregate_type`, `aggregate_id`, `event_type`, `payload`, `status`, `retry_count`
- 상태: `PENDING`, `IN_FLIGHT`, `COMPLETED`, `FAILED`
- 인덱스: `(status, retry_count)` (`ix_outbox_events_status_retry`)

### notification_provider_codes (v2)
- 알림별 provider 응답 코드 이력 보관
- `notification_id`, `provider`, `provider_status_code`, `provider_response`, `captured_at`
- 인덱스: `(notification_id)`

## 마이그레이션 레이어
- v1: baseline schema 생성 (`001_initial_persistence_schema`)
- v2: 운영 관측/수동 대응 필드 보강 (`002_add_operability_fields`)
- v3: 프로필 신체 수치 정합 (`003_god38_schema_alignment`)
- v4: 요약 집계 스냅샷 테이블 추가 (`004_add_summary_aggregates`)
- v5: 운동 중량 컬럼 실수형 정합 (`005_god33_weight_columns_float`)
  - `exercise_sessions.target_weight_kg`: `Integer -> Float`
  - `exercise_set_states.performed_weight_kg`: `Integer -> Float`

## 운영 점검 포인트
- `GOD-33` 완료 시 `manual review`, webhook 파싱 버전, 알림 실패 추적 쿼리가 모두 동작해야 한다.
- 수동 개입이 필요한 알림/웹훅 레코드 조회는 `reason_code` + `memo` + `updated_at` 기준으로 정합성 있게 확인 가능해야 한다.
- 운동 plan 생성 충돌 매핑은 `uq_exercise_plans_user_target_date_active` 위반일 때만 `conflict`로 처리하고,
  FK 위반 등 다른 무결성 오류는 일반 DB 오류로 분리한다.
- 운동 관련 중량 데이터는 소수점 값 저장/조회 시 손실 없이 유지되어야 한다.
