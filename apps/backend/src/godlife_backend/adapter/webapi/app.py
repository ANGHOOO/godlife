"""FastAPI application factory for the backend web API."""

from __future__ import annotations

from fastapi import FastAPI
from godlife_backend.adapter.webapi.routers.health import router as health_router
from godlife_backend.adapter.webapi.routers.notifications import (
    router as notifications_router,
)
from godlife_backend.adapter.webapi.routers.plans import router as plans_router
from godlife_backend.adapter.webapi.routers.reading import router as reading_router
from godlife_backend.adapter.webapi.routers.summary import router as summary_router
from godlife_backend.adapter.webapi.routers.webhooks import router as webhooks_router


def create_app() -> FastAPI:
    app = FastAPI(title="GodLife API", version="0.1.0")
    app.include_router(health_router)
    app.include_router(plans_router)
    app.include_router(notifications_router)
    app.include_router(reading_router)
    app.include_router(summary_router)
    app.include_router(webhooks_router)
    return app


app = create_app()
