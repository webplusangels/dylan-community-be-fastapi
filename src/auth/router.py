from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import dependencies, schemas, service
from src.core.config import settings
from src.db.session import get_async_db
from src.users import models

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token",
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
    summary="액세스 토큰 발급",
    description="사용자의 이메일과 비밀번호로 인증 후 JWT 액세스 토큰을 발급합니다.",
)
async def login_for_access_token(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    사용자 인증 및 JWT 액세스 토큰 발급 엔드포인트입니다.

    :param db: 비동기 데이터베이스 세션
    :param form_data: OAuth2 비밀번호 요청 폼 데이터 (username, password)
    :return: JWT 액세스 토큰과 토큰 타입
    """
    # 사용자 인증
    user = await service.authenticate_user(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 액세스 토큰 발급
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expiry = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    token_data = {
        "sub": str(user.id),
        "roles": "admin" if user.is_admin else "user",
    }
    access_token = service.create_access_token(
        data=token_data, expires_delta=access_token_expiry
    )
    refresh_token = service.create_refresh_token(
        data=token_data, expires_delta=refresh_token_expiry
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
    summary="액세스 토큰 갱신",
    description="현재 액세스 토큰을 갱신하여 새로운 JWT 액세스 토큰과 리프레시 토큰을 발급합니다.",
)
async def refresh_token(
    current_user: Annotated[
        models.User, Depends(dependencies.get_current_user_from_refresh_token)
    ],
):
    """
    리프레시 토큰으로 새로운 리프레시 토큰과 액세스 토큰을 발급하는 엔드포인트입니다.

    :param current_user: 현재 인증된 사용자 모델
    :return: 새로운 JWT 액세스 토큰과 리프레시 토큰
    """
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expiry = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    token_data = {
        "sub": str(current_user.id),
        "roles": "admin" if current_user.is_admin else "user",
    }
    new_access_token = service.create_access_token(
        data=token_data, expires_delta=access_token_expiry
    )
    new_refresh_token = service.create_refresh_token(
        data=token_data, expires_delta=refresh_token_expiry
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
