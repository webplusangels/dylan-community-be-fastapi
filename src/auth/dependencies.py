from typing import Annotated, Any, Mapping

from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.base import SecurityBase
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud as auth_crud
from src.core.config import settings
from src.db.session import get_async_db
from src.users import crud, models


class RefreshTokenBearer(SecurityBase):
    """
    OAuth2PasswordBearer를 확장하여 리프레시 토큰을 위한 보안 스키마입니다.
    """

    def __init__(self):
        self.scheme_name = "RefreshTokenBearer"
        self.model = APIKey(
            **{
                "in": APIKeyIn.header,
                "name": "X-Refresh-Token",
                "description": "리프레시 토큰을 포함하는 헤더입니다. Bearer 접두사를 사용하지 않습니다.",
            }
        )

    async def __call__(self, request: Request) -> str:
        """
        X-Refresh-Token 헤더에서 리프레시 토큰을 추출합니다.

        :param request: FastAPI 요청 객체
        :return: 리프레시 토큰 문자열 또는 None
        """
        refresh_token = request.headers.get("X-Refresh-Token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="리프레시 토큰이 필요합니다.",
            )
        if refresh_token.startswith("Bearer "):
            refresh_token = refresh_token[7:]

        return refresh_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
refreshTokenBearer = RefreshTokenBearer()


async def _get_user_from_token(
    token: str,
    secret_key: str,
    db: AsyncSession,
) -> tuple[models.User, dict[str, Any]]:
    """
    JWT 토큰을 디코딩하여 사용자 정보를 반환합니다.
    내부 함수로 사용되며, 액세스 토큰과 리프레시 토큰 모두에 사용됩니다.

    :param token: JWT 액세스 토큰 또는 리프레시 토큰
    :param secret_key: JWT 서명에 사용되는 비밀 키
    :param db: 비동기 데이터베이스 세션
    :return: 인증된 사용자 모델
    :raises HTTPException: 토큰이 유효하지 않거나 사용자가 존재하지 않는 경우 401 에러 발생
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        raw_payload: Mapping[str, Any] = jwt.decode(
            token, secret_key, algorithms=[settings.ALGORITHM]
        )
        payload = dict(raw_payload)
        user_id: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
        if await auth_crud.is_token_blocked(db, jti=jti):
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    user = await crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user, payload


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> models.User:
    """
    JWT 토큰을 디코딩하여 현재 인증된 사용자를 반환합니다.

    :param token: OAuth2PasswordBearer에서 추출한 JWT 액세스 토큰
    :param db: 비동기 데이터베이스 세션
    :return: 인증된 사용자 모델
    """
    user, _ = await _get_user_from_token(token, settings.SECRET_KEY, db)
    return user


async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    """
    인증된 사용자 중 현재 활성화된 사용자를 반환합니다.

    :param current_user: get_current_user에서 반환된 사용자 모델
    :return: 활성화된 사용자 모델
    :raises HTTPException: 사용자가 비활성화된 경우 403 에러 발생
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="사용자가 비활성화되었습니다.",
        )
    return current_user


async def get_current_user_from_refresh_token(
    request: Request,
    token: Annotated[str, Depends(refreshTokenBearer)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> models.User:
    """
    리프레시 토큰을 디코딩하여 현재 인증된 사용자를 반환합니다.

    :param request: FastAPI 요청 객체
    :param token: OAuth2PasswordBearer에서 추출한 JWT 리프레시 토큰
    :param db: 비동기 데이터베이스 세션
    :return: 인증된 사용자 모델
    """
    user, payload = await _get_user_from_token(token, settings.REFRESH_SECRET_KEY, db)
    request.state.decoded_refresh_token_payload = payload  # type: ignore
    return user
