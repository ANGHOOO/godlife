"""Authentication-oriented helpers for web API."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from godlife_backend.adapter.webapi.dependencies import get_user_repository
from godlife_backend.domain.entities import User
from godlife_backend.domain.ports import UserRepository
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthResolveRequest(BaseModel):
    kakao_user_id: str
    name: str | None = None


class AuthResolveResponse(BaseModel):
    user_id: UUID
    kakao_user_id: str
    name: str


@router.post(
    "/resolve",
    response_model=AuthResolveResponse,
    status_code=status.HTTP_200_OK,
)
def resolve_user(
    request: AuthResolveRequest,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthResolveResponse:
    kakao_user_id = request.kakao_user_id.strip()
    if not kakao_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="kakao_user_id is required",
        )

    user = repository.get_by_kakao_user_id(kakao_user_id=kakao_user_id)
    if user is None:
        user = repository.save(
            User(
                kakao_user_id=kakao_user_id,
                name=(request.name or "").strip() or "Kakao User",
            )
        )

    return AuthResolveResponse(
        user_id=user.id,
        kakao_user_id=user.kakao_user_id,
        name=user.name,
    )
