# GodLife

GodLife는 운동 기록 자동화와 독서 리마인드를 결합한 습관 성장 앱입니다.

## 실행 가이드
### 1) PostgreSQL 컨테이너만 띄워서 로컬 앱 실행
1. PostgreSQL 컨테이너 실행
   - `docker run --name godlife-postgres -e POSTGRES_DB=godlife -e POSTGRES_USER=godlife -e POSTGRES_PASSWORD=godlife -p 5432:5432 -d postgres:16-alpine`
2. 백엔드 의존성 동기화
   - `uv sync`
3. 백엔드 마이그레이션
   - `cd apps/backend`
   - `export DATABASE_URL=postgresql+psycopg://godlife:godlife@127.0.0.1:5432/godlife`
   - `uv run alembic -c alembic.ini upgrade head`
4. 백엔드 실행(프로젝트 루트)
   - `export DATABASE_URL=postgresql+psycopg://godlife:godlife@127.0.0.1:5432/godlife`
   - `uv run python apps/backend/main.py`
5. 프론트 실행
   - `cd apps/frontend`
   - `pnpm install`
   - `BACKEND_BASE_URL=http://127.0.0.1:8000 pnpm dev`

### 2) Docker Compose로 frontend/backend/postgresql 동시 실행 (개발)
1. 환경 템플릿 복사
   - `cp .env.example .env`
2. 서비스 실행
   - `docker compose -f compose.yaml -f compose.dev.yaml up --build`
   - compose 실행 시 `backend-migrate`와 `backend-seed`가 선행되어 스키마/기본 사용자(`00000000-0000-0000-0000-000000000001`)를 준비합니다.
3. 확인 URL
   - 프론트: `http://127.0.0.1:3000`
   - 백엔드: `http://127.0.0.1:8000/healthz`
   - 프론트 BFF health: `http://127.0.0.1:3000/api/health`

### 3) Docker Compose 운영 배포 모드
1. 배포 이미지 태그 지정
   - `BACKEND_IMAGE=<registry>/godlife-backend:<tag>`
   - `BACKEND_MIGRATE_IMAGE=<registry>/godlife-backend-migrate:<tag>`
   - `FRONTEND_IMAGE=<registry>/godlife-frontend:<tag>`
2. 운영 서비스 실행
   - `docker compose -f compose.yaml -f compose.prod.yaml up -d`

## 백엔드 공통 기술 스택
- 패키지/의존성 관리: uv
- 웹 프레임워크: FastAPI
- DB: Docker PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic
- 테스트: pytest
- 타입: ty==0.0.17
- 코드 포맷/린트: ruff
- Git 훅: pre-commit
- CI/CD: GitHub Actions

## 로컬 개발 루틴
- 의존성 동기화: `uv sync`
- 코드 정리: `uv run ruff check .` / `uv run ruff format .`
- 타입 체크: `uv run ty check --extra-search-path apps/backend/src .`
- 테스트: `uv run pytest`
- 마이그레이션: `cd apps/backend` 후 `uv run alembic -c alembic.ini upgrade head`
- Git hook 설치(처음 1회): `bash scripts/setup-git-hooks.sh`
- 커밋 규칙:
  - 위 설정 후 `git commit`마다 `pre-commit`이 자동으로 실행되어 `ruff-check`/`ruff-format`/`ty-check`/`pytest`를 검증합니다.
  - 훅 실행을 우회하려면 `--no-verify`를 사용해야 합니다(권장하지 않음).
- 커밋 전 수동 검증: `uv run pre-commit run --all-files`
- pre-commit `ty-check` 동작 방식:
  - `pre-commit`는 자체 Python 환경(격리 환경)에서 실행됩니다.
  - 동일하게 `apps/backend` 경로에 설치된 의존성(`uv sync`)만으로는 훅 환경에서 즉시 해석되지 않으므로,
    `.pre-commit-config.yaml`의 `ty-check`에 `fastapi`, `pydantic`, `pytest`, `alembic`, `sqlalchemy`, `psycopg[binary]`를 명시적으로 선언했습니다.
  - 타입 검증은 CI와 동일하게 `--extra-search-path apps/backend/src`를 사용합니다.
  - 이로 인해 CI에서 `unresolved-import`로 `fastapi`/`pydantic`/`pytest`가 탐지되는 문제를 방지합니다.

## 브랜치 전략 (Git Flow)
- 운영 브랜치: `main`
- 통합 브랜치: `develop`
- 작업 브랜치: `feature/<Linear-Issue-키>-<설명>`
- 기본 플로우:
  - feature 브랜치에서 기능 개발
  - 로컬 테스트 완료 후 `develop`로 PR 생성 및 Merge
  - `develop`는 스테이징/통합 기준으로 운영 검증
  - 배포 후보는 `develop -> main` PR로 반영
- CI 정책:
  - `develop`/`main` 기준 PR 및 push에서 공통 검증(ruff/format/type/pytest/pre-commit) 실행
  - `develop` 대상 PR은 반드시 `feature/*` 브랜치에서만 허용
  - `main` 대상 PR은 반드시 `develop`에서만 허용

## 커밋 메시지와 Linear 이슈 링크
- 커밋 메시지 권장 형식:
  - `<타입>: <변경 요약> (#GOD-33)`
  - 예: `feat: 운동/독서 상태 전이 테스트 추가 (#GOD-33)`
- 현재 사용 중인 Linear 워크스페이스:
  - `https://linear.app/godlife`
- GitHub 저장소에서 `#GOD-33` 링크를 자동 클릭 가능하게 하려면 GitHub Settings > General > Features > Autolinks references에서 다음처럼 등록:
  - Prefix: `#`
  - Target URL: `https://linear.app/godlife/issue/$1`
  - 결과: 커밋 메시지의 `#GOD-33`이 `https://linear.app/godlife/issue/GOD-33`로 이동

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
- `docs/persistence-schema-contract.md`
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
- `docs/next-iteration-pr-plan.md`
- `docs/consistency-fix-notes.md`
