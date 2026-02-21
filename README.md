# GodLife

GodLife는 운동 기록 자동화와 독서 리마인드를 결합한 습관 성장 앱입니다.

## 실행
- `uv sync`
- `uv run python main.py`

## 백엔드 공통 기술 스택
- 패키지/의존성 관리: uv
- 웹 프레임워크: FastAPI
- DB: Docker PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic
- 테스트: pytest
- 타입: ty==0.9.5
- 코드 포맷/린트: ruff
- Git 훅: pre-commit
- CI/CD: GitHub Actions

## 로컬 개발 루틴
- 의존성 동기화: `uv sync`
- 코드 정리: `uv run ruff check .` / `uv run ruff format .`
- 타입 체크: `uv run ty check .`
- 테스트: `uv run pytest`
- 마이그레이션: `uv run alembic upgrade head`

## 브랜치 전략 (Git Flow)
- 운영 브랜치: `main`
- 통합 브랜치: `develop`
- 작업 브랜치: `feature/GOD-ISSUE-요약`
- 기본 플로우:
  - feature 브랜치에서 기능 개발
  - 로컬 테스트 완료 후 `develop`로 PR 생성 및 Merge
  - `develop`는 스테이징/통합 기준으로 운영 검증
  - 배포 후보는 `develop -> main` PR로 반영
- CI 정책:
  - `develop`/`main` 기준 PR 및 push에서 공통 검증(ruff/format/type/pytest/pre-commit) 실행
  - `develop` 대상 PR은 반드시 `feature/*` 브랜치에서만 허용
  - `main` 대상 PR은 반드시 `develop`에서만 허용

## 문서/AI 협업 정책
- AI 협업 시 공식 API 문서/라이브러리 문서는 Context7 기반 질의로 최신 규칙을 먼저 확인한다.
- 변경 전후로 `docs/*`와 `apps/backend/docs/*`에 근거를 간결히 남긴다.

## 문서 지도
### PRD 및 공통
- `docs/PRD.md`
- `docs/architecture-overview.md`
- `docs/feature-breakdown.md`
- `docs/api-spec.md`
- `docs/state-and-policy.md`
- `docs/scheduling-notification-policy.md`
- `docs/observability-runbook.md`
- `docs/testing-plan.md`

### 백엔드
- `apps/backend/docs/development_guide.md`
- `apps/backend/docs/domain_model.md`
- `apps/backend/docs/backend-implementation-spec.md`
- `apps/backend/docs/data-model.md`
- `apps/backend/docs/repository-and-persistence-contract.md`
- `apps/backend/docs/messaging-webhook-idempotency.md`
- `apps/backend/docs/scheduler-worker-spec.md`
- `apps/backend/docs/deployment-operations.md`
- `apps/backend/docs/testing-strategy.md`

### 프론트엔드
- `apps/frontend/docs/frontend-implementation-spec.md`
- `apps/frontend/docs/user-flow-spec.md`
- `apps/frontend/docs/ui-state-and-sync.md`
- `apps/frontend/docs/error-and-empty-state-policy.md`
- `apps/frontend/docs/accessibility-performance-spec.md`
- `apps/frontend/docs/frontend-testing.md`

- `docs/consistency-checklist.md`
- `docs/implementation-roadmap.md`
- `docs/consistency-fix-notes.md`
