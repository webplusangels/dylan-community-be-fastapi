import uuid
from datetime import datetime, timedelta, timezone
from typing import cast

from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud as auth_crud
from src.core.config import settings
from src.core.security import verify_password
from src.users import crud, models


def _create_token(
    data: dict, expires_delta: timedelta, secret_key: str, algorithm: str
) -> str:
    """
    JWT 토큰을 생성하는 내부 함수입니다.
    :param data: JWT 페이로드에 포함될 데이터
    :param expires_delta: 토큰 만료 시간 (timedelta 객체)
    :param secret_key: JWT 서명에 사용할 비밀 키
    :param algorithm: JWT 서명 알고리즘
    :return: 생성된 JWT 토큰 문자열
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
        }
    )
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


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
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return _create_token(
        data=data,
        expires_delta=delta,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


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
    delta = expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    return _create_token(
        data=data,
        expires_delta=delta,
        secret_key=settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


async def logout_user(db: AsyncSession, jti: str, expires_at: datetime) -> None:
    """
    사용자를 로그아웃하고 토큰을 블락리스트에 추가합니다.

    :param db: 비동기 데이터베이스 세션
    :param jti: 토큰의 고유 식별자 (jti)
    :param expires_at: 토큰의 만료 시간
    """
    await auth_crud.add_token_to_blocklist(db=db, jti=jti, expires_at=expires_at)
