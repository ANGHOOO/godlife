FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY apps/backend ./apps/backend

EXPOSE 8000

CMD [".venv/bin/python", "apps/backend/main.py"]
