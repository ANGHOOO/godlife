"""GodLife backend application package."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_app() -> "FastAPI":
    from godlife_backend.adapter.webapi.app import create_app as _create_app

    return _create_app()


__all__ = ["create_app"]
