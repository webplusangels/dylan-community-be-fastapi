from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
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
    old_refresh_token: Annotated[str, Depends(dependencies.refreshTokenBearer)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    """
    리프레시 토큰으로 새로운 리프레시 토큰과 액세스 토큰을 발급하는 엔드포인트입니다.

    :param current_user: 현재 인증된 사용자 모델
    :param old_refresh_token: 기존 리프레시 토큰
    :param db: 비동기 데이터베이스 세션
    :return: 새로운 JWT 액세스 토큰과 리프레시 토큰
    """
    try:
        payload = jwt.decode(
            old_refresh_token,
            settings.REFRESH_SECRET_KEY,
            algorithms=settings.ALGORITHM,
        )
        old_jti = payload.get("jti")
        old_exp = payload.get("exp")
        if old_jti and old_exp:
            expires_at = datetime.fromtimestamp(old_exp, tz=timezone.utc)
            await service.logout_user(db=db, jti=old_jti, expires_at=expires_at)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

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


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="로그아웃",
    description="현재 사용자의 액세스 토큰을 블락리스트에 추가하여 로그아웃 처리합니다.",
)
async def logout(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    access_token: Annotated[str, Depends(dependencies.oauth2_scheme)],
    refresh_token: Annotated[str, Depends(dependencies.refreshTokenBearer)],
):
    """
    현재 사용자의 액세스 토큰을 블락리스트에 추가하여 로그아웃 처리하는 엔드포인트입니다.

    :param db: 비동기 데이터베이스 세션
    :param access_token: OAuth2 액세스 토큰
    :param refresh_token: OAuth2 리프레시 토큰
    :raises HTTPException: 유효하지 않은 토큰인 경우 401 에러 발생
    """
    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti and exp:
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            await service.logout_user(db=db, jti=jti, expires_at=expires_at)

    except JWTError:
        # 토큰이 유효하지 않은 경우, 이미 인증 불가능이므로 예외를 발생시키지 않습니다.
        pass

    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti and exp:
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            await service.logout_user(db=db, jti=jti, expires_at=expires_at)

    except JWTError:
        pass

    return Response(status_code=status.HTTP_204_NO_CONTENT)
