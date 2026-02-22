from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from godlife_backend.adapter.test_doubles import InMemoryUserRepository
from godlife_backend.adapter.webapi.routers.auth import (
    AuthResolveRequest,
    AuthResolveResponse,
    resolve_user,
)
from godlife_backend.domain.entities import User


def test_resolve_user_returns_existing_user_id() -> None:
    repository = InMemoryUserRepository()
    user = repository.save(
        User(
            id=uuid4(),
            kakao_user_id="kakao-1",
            name="기존 사용자",
        )
    )

    response = resolve_user(
        request=AuthResolveRequest(kakao_user_id="kakao-1", name="ignored"),
        repository=repository,
    )

    assert isinstance(response, AuthResolveResponse)
    assert response.user_id == user.id
    assert response.kakao_user_id == "kakao-1"
    assert response.name == "기존 사용자"


def test_resolve_user_creates_missing_user() -> None:
    repository = InMemoryUserRepository()

    response = resolve_user(
        request=AuthResolveRequest(
            kakao_user_id="kakao-new",
            name="새 사용자",
        ),
        repository=repository,
    )

    assert isinstance(response, AuthResolveResponse)
    assert response.kakao_user_id == "kakao-new"
    assert response.name == "새 사용자"
    stored = repository.get_by_kakao_user_id("kakao-new")
    assert stored is not None
    assert isinstance(stored.id, UUID)


def test_resolve_user_rejects_empty_kakao_user_id() -> None:
    with pytest.raises(HTTPException) as exc_info:
        resolve_user(
            request=AuthResolveRequest(kakao_user_id="", name="empty"),
            repository=InMemoryUserRepository(),
        )

    assert exc_info.value.status_code == 400
