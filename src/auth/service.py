from datetime import datetime, timedelta, timezone
from typing import cast

from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import verify_password
from src.users import crud, models


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> models.User | None:
    """
    사용자의 이메일과 비밀번호로 인증을 시도합니다.

    :param db: 비동기 데이터베이스 세션
    :param email: 사용자 이메일
    :param password: 사용자 비밀번호
    :return: 인증된 사용자 모델 또는 None
    """
    db_user = await crud.get_user_by_email(db=db, email=email)
    if not db_user:
        return None

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="사용자가 비활성화되었습니다.",
        )

    if not verify_password(password, cast(str, db_user.hashed_password)):
        return None

    return db_user


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    JWT 액세스 토큰을 생성합니다.

    :param data: JWT 페이로드에 포함될 데이터
    :param expires_delta: 토큰 만료 시간 (초 단위)
    :return: 생성된 JWT 액세스 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
    )

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    JWT 리프레시 토큰을 생성합니다.

    :param data: JWT 페이로드에 포함될 데이터
    :param expires_delta: 토큰 만료 시간 (초 단위)
    :return: 생성된 JWT 리프레시 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
    )

    encoded_jwt = jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt
