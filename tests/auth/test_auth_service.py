from datetime import datetime, timedelta, timezone
from time import time
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from jose import jwt

from src.auth import service
from src.core.config import settings
from src.core.security import hash_password
from src.users import models as user_models


@pytest.mark.asyncio
async def test_authenticate_user_success(mocker):
    """
    사용자 인증 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    test_user = user_models.User(
        email="test@example.com",
        username="testuser",
        is_active=True,
    )

    mocker.patch(
        "src.users.crud.get_user_by_email",
        return_value=test_user,
    )
    mocker.patch("src.auth.service.verify_password", return_value=True)

    # Act
    authenticated_user = await service.authenticate_user(
        db=mock_db, email=test_user.email, password="plainpassword123"
    )

    # Assert
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email


@pytest.mark.asyncio
async def test_authenticate_user_failure_wrong_password(mocker):
    """
    사용자 인증 실패 테스트(잘못된 비밀번호)
    """
    # Arrange
    mock_db = AsyncMock()
    test_user = user_models.User(
        email="test@example.com",
        hashed_password=hash_password("plainpassword123"),
        is_active=True,
    )

    mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
    mocker.patch("src.auth.service.verify_password", return_value=False)

    # Act
    authenticated_user = await service.authenticate_user(
        db=mock_db, email=test_user.email, password="wrongpassword123"
    )

    # Assert
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_user_failure_inactive_user(mocker):
    """
    사용자 인증 실패 테스트(비활성화된 사용자)
    """
    # Arrange
    mock_db = AsyncMock()
    test_user = user_models.User(
        email="test@example.com",
        hashed_password=hash_password("plainpassword123"),
        is_active=False,  # 비활성화된 사용자
    )

    mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
    mocker.patch("src.auth.service.verify_password", return_value=True)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate_user(
            db=mock_db, email=test_user.email, password="plainpassword123"
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "사용자가 비활성화되었습니다."


@pytest.mark.asyncio
async def test_authenticate_user_failure_user_not_found(mocker):
    """
    사용자 인증 실패 테스트(사용자 없음)
    """
    # Arrange
    mock_db = AsyncMock()
    test_user = user_models.User(
        id="uuid",
        email="test@example.com",
        hashed_password=hash_password("plainpassword123"),
    )

    mocker.patch("src.users.crud.get_user_by_email", return_value=None)

    # Act
    authenticated_user = await service.authenticate_user(
        db=mock_db, email=test_user.email, password="plainpassword123"
    )

    # Assert
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_create_access_token(mocker):
    """
    JWT 액세스 토큰 생성 테스트
    """
    # Arrange
    data = {"sub": "testuser", "roles": ["user"]}
    expires_delta = timedelta(minutes=30)

    # Act
    token = service.create_access_token(
        data=data,
        expires_delta=expires_delta,
    )

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0

    decoded_token = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded_token["sub"] == data["sub"]
    assert decoded_token["roles"] == data["roles"]
    assert "exp" in decoded_token  # 만료 시간 포함 여부 확인
    assert "iat" in decoded_token  # 발급 시간 포함 여부 확인
    assert "jti" in decoded_token  # JWT ID 포함 여부 확인

    # 만료 시간 검증
    expected_exp = time() + (30 * 60)
    assert abs(decoded_token["exp"] - expected_exp) < 60


@pytest.mark.asyncio
async def test_create_refresh_token(mocker):
    """
    JWT 리프레시 토큰 생성 테스트
    """
    # Arrange
    data = {"sub": "testuser", "roles": ["user"]}
    expires_delta = timedelta(minutes=60)

    # Act
    token = service.create_refresh_token(
        data=data,
        expires_delta=expires_delta,
    )

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0

    decoded_token = jwt.decode(
        token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded_token["sub"] == data["sub"]
    assert decoded_token["roles"] == data["roles"]
    assert "exp" in decoded_token
    assert "iat" in decoded_token
    assert "jti" in decoded_token

    expected_exp = time() + (60 * 60)  # 60분
    assert abs(decoded_token["exp"] - expected_exp) < 60


@pytest.mark.asyncio
async def test_create_refresh_token_default_expiry():
    """
    리프레시 토큰 기본 만료시간 테스트
    """
    data = {"sub": "testuser"}

    token = service.create_refresh_token(data=data)  # expires_delta 없음

    decoded = jwt.decode(
        token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    # 기본 만료시간 확인
    expected_exp = time() + (settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60)
    assert abs(decoded["exp"] - expected_exp) < 60


@pytest.mark.asyncio
async def test_logout_user(mocker):
    """
    사용자 로그아웃 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    jti = "test_jti"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    mock_add_token_to_blocklist = mocker.patch(
        "src.auth.crud.add_token_to_blocklist", return_value=None
    )

    # Act
    await service.logout_user(db=mock_db, jti=jti, expires_at=expires_at)

    # Assert
    mock_add_token_to_blocklist.assert_called_once_with(
        db=mock_db, jti=jti, expires_at=expires_at
    )


@pytest.mark.asyncio
async def test_logout_user_invalid_jti(mocker):
    """
    로그아웃 시 유효하지 않은 JTI 처리 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    jti = "invalid_jti"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    mocker.patch(
        "src.auth.crud.add_token_to_blocklist",
        side_effect=HTTPException(status_code=400, detail="Invalid JTI"),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.logout_user(db=mock_db, jti=jti, expires_at=expires_at)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid JTI"


@pytest.mark.asyncio
async def test_logout_user_expired_token(mocker):
    """
    로그아웃 시 만료된 토큰 처리 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    jti = "expired_jti"
    expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

    mocker.patch(
        "src.auth.crud.add_token_to_blocklist",
        side_effect=HTTPException(status_code=400, detail="토큰이 만료되었습니다."),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.logout_user(db=mock_db, jti=jti, expires_at=expires_at)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "토큰이 만료되었습니다."


@pytest.mark.asyncio
async def test_logout_user_already_blocked(mocker):
    """
    로그아웃 시 이미 블락리스트에 있는 토큰 처리 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    jti = "already_blocked_jti"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    mocker.patch(
        "src.auth.crud.add_token_to_blocklist",
        side_effect=HTTPException(
            status_code=400, detail="이미 블락리스트에 있습니다."
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.logout_user(db=mock_db, jti=jti, expires_at=expires_at)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "이미 블락리스트에 있습니다."
