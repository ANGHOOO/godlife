# 배포 및 운영 가이드

## 1. 배포 전 체크
- 환경변수: DB URL, Redis, Kakao 토큰, LLM 키, 시크릿
- API 명세와 라우터 동기화
- DB 마이그레이션 dry-run
- persistence schema 최신 리비전 확인 (`uv run alembic -c apps/backend/alembic.ini current`)
- 신규 테이블/인덱스/유니크 제약 검증 (`uv run alembic -c apps/backend/alembic.ini upgrade head` 실행 후 스키마 점검)

## 2. 배포 절차
1. DB 마이그레이션
2. API 서버 배포
3. 스케줄러/워커 배포
4. Kakao webhook URL 검증
5. smoke 테스트(health, plan 생성, 알림 큐 등록)
6. migration 검증 쿼리:
   - `users.id` PK 존재
   - `notifications.idempotency_key` 유니크 제약 존재
   - `webhook_events.provider/event_id` 및 `provider/idempotency_key` 유니크 제약 존재

## 3. 운영 점검
- `/healthz`, `/readyz` 2회 확인
- 일일 알림 1건, webhook 수신 1건 테스트
- 운동 plan 생성 검증
  - `POST /plans/generate` 성공 응답이 `201`인지 확인
  - `plan_source`/`source` 중 하나를 보냈을 때 `source`가 `rule|llm`으로 정규화되는지 확인
  - 동일 `user_id + target_date` 재요청 시 `409 conflict` 확인
  - `plan_source=""` 또는 `source=""` 요청 시 `400 validation` 확인
- manual review 큐 empty 확인
- `notification_provider_codes` 최근 수집 건 수집률 확인 (v2 migration 적용 여부 포함)

## 4. 릴리즈 가드레일
- LLM 비활성화 플래그
- 규칙 기반 fallback 강제 모드
- 알림 수율 급감 시 발송 제한치

## 5. 롤백 기준
- 요약 지표 오차, manual review 급증, 지속 실패율 임계 초과 시 즉시 이전 버전 복귀

## 6. 유지보수 로그
- 배포 로그, 마이그레이션 로그, webhook 발송 추적 로그 보관

## 7. GOD-33 마이그레이션 체크리스트
- 단계 1: `uv run alembic -c apps/backend/alembic.ini upgrade head`
- 단계 2: `uv run alembic -c apps/backend/alembic.ini history`로 `001_initial_persistence_schema -> 002_add_operability_fields` 연속성 확인
- 단계 3: 필수 제약 점검
  - `SELECT conname FROM pg_constraint WHERE conname LIKE '%notifications%'`
  - `SELECT indexname FROM pg_indexes WHERE tablename IN ('exercise_set_states', 'notifications', 'webhook_events')`
- 단계 4: 롤백 검증
  - `uv run alembic -c apps/backend/alembic.ini downgrade -1`
  - `uv run alembic -c apps/backend/alembic.ini upgrade head`
- 단계 5: v2 운영 컬럼 조회
  - `SELECT column_name FROM information_schema.columns WHERE table_name='notifications' AND column_name IN ('reason_code', 'provider_response_code', 'failure_reason', 'last_error_at')`
  - `SELECT column_name FROM information_schema.columns WHERE table_name='webhook_events' AND column_name IN ('schema_version', 'signature_state', 'retry_count')`
