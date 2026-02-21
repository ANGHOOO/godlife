# 언어 & 소통
- 항상 한국어로 대답해줘
- 코드 수정 전에는 먼저 계획을 알려줘
- 확신이 없으면 진행하기 전에 물어봐줘

# 작업 규칙 (IMPORTANT — 반드시 지킬 것)
- 라이브러리/API 문서, 코드 생성, 설정 또는 구성 단계가 필요할 때, 일일이 요청하지 않더라도 항상 Context7 MCP를 사용 할 것.
- .env 파일은 절대 읽거나 수정하지 말 것
- 파일 삭제 전 반드시 확인 요청할 것
- 커밋 메시지는 한국어로 작것할 것
- 새로 생성/변경한 코드에 대해 **로컬 점검을 선행**하고 실패 소지를 확인할 것

# 코드 스타일
- 테스트 없이 새 기능 추가하지 않기
- 변경 전 git diff로 현재 상태 먼저 확인하기
- `ruff`는 `ruff check .`와 `ruff format .` 실패가 없어야 함

# CI 재현/방지 규칙
- 마이그레이션/모듈 신규 추가 시 `ty`가 모듈 경로를 못 찾는 문제가 자주 발생하므로,
  - `uv run ty check --extra-search-path apps/backend/src .`
  - 동일 형식으로 CI에서도 실행되도록 관리
- CI 실행 순서는 다음을 기준으로 맞춘다.
  1. `uv run ruff check .`
  2. `uv run ruff format --check .`
  3. `uv run ty check --extra-search-path apps/backend/src .`
  4. `uv run pytest`
- `.pre-commit-config.yaml`에서 `ty-check`는 추가 import 경로(`--extra-search-path apps/backend/src`)를 설정하고
  필요한 타입 의존성(`alembic`, `sqlalchemy`, `psycopg[binary]`)을 포함한다.
- CI/로컬에서 `pre-commit`은 캐시 경로/네트워크 제약으로 실패할 수 있으므로, 장애 재현 시
  - 캐시 경로(`PRE_COMMIT_HOME`) 분리
  - 네트워크 접근이 제한된 환경에서는 해당 단계 원인 분리 후 기록
  - 가능한 경우 `ruff/ty/pytest`로 동일 신호를 먼저 검증한다.
