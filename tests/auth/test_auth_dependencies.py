from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.auth import dependencies as auth_deps
from src.auth import exceptions as auth_exceptions
from src.users import models as user_models


@pytest.mark.asyncio
async def test_get_current_active_user_success():
    """활성 사용자일 때 get_current_active_user가 사용자 반환"""
    user = user_models.User(id="u1", is_active=True)

    result = await auth_deps.get_current_active_user(current_user=user)

    assert result is user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """비활성 사용자이면 HTTPException 403 발생"""
    user = user_models.User(id="u2", is_active=False)

    with pytest.raises(HTTPException) as exc_info:
        await auth_deps.get_current_active_user(current_user=user)

    assert exc_info.value.status_code == 403
    assert "사용자가 비활성화되었습니다." in exc_info.value.detail


@pytest.mark.asyncio
async def test__get_user_from_token_success(mocker):
    """_get_user_from_token이 정상적으로 User와 payload를 반환하는지 테스트"""
    mock_db = AsyncMock()
    token = "valid-token"
    secret = "secret"
    payload = {"sub": "user-1", "jti": "jti-1", "token_version": 0}

    # jwt.decode이 payload를 반환하도록 패치
    mocker.patch("src.auth.dependencies.jwt.decode", return_value=payload)

    # users crud.get_user이 해당 사용자 반환
    mocked_user = user_models.User(id=payload["sub"], token_version=0, is_active=True)
    mock_get_user = mocker.patch("src.users.crud.get_user", return_value=mocked_user)

    # auth_crud.is_token_blocked은 False 반환
    mocker.patch("src.auth.crud.is_token_blocked", return_value=False)

    user, returned_payload = await auth_deps._get_user_from_token(
        token=token, secret_key=secret, db=mock_db
    )

    assert user is mocked_user
    assert returned_payload["sub"] == payload["sub"]
    mock_get_user.assert_called()


@pytest.mark.asyncio
async def test__get_user_from_token_missing_fields_raises_invalid(mocker):
    """jwt.decode가 필수 필드를 반환하지 않으면 InvalidTokenError 발생"""
    mock_db = AsyncMock()
    token = "bad-token"
    secret = "secret"
    payload = {"sub": None}  # jti가 없음

    mocker.patch("src.auth.dependencies.jwt.decode", return_value=payload)

    with pytest.raises(auth_exceptions.InvalidTokenError):
        await auth_deps._get_user_from_token(token=token, secret_key=secret, db=mock_db)


@pytest.mark.asyncio
async def test__get_user_from_token_blocked_token_raises(mocker):
    """토큰이 블락된 경우 TokenBlockedError 발생"""
    mock_db = AsyncMock()
    token = "blocked-token"
    secret = "secret"
    payload = {"sub": "user-2", "jti": "jti-blocked", "token_version": 0}

    mocker.patch("src.auth.dependencies.jwt.decode", return_value=payload)
    mocker.patch(
        "src.users.crud.get_user",
        return_value=user_models.User(id=payload["sub"], token_version=0),
    )
    mocker.patch("src.auth.crud.is_token_blocked", return_value=True)

    with pytest.raises(auth_exceptions.TokenBlockedError):
        await auth_deps._get_user_from_token(token=token, secret_key=secret, db=mock_db)


@pytest.mark.asyncio
async def test__get_user_from_token_token_version_expired(mocker):
    """토큰의 token_version이 DB의 token_version보다 작으면 TokenExpiredError 발생"""
    mock_db = AsyncMock()
    token = "expired-token"
    secret = "secret"
    payload = {"sub": "user-3", "jti": "jti-3", "token_version": 0}

    # jwt.decode -> payload
    mocker.patch("src.auth.dependencies.jwt.decode", return_value=payload)

    # DB의 user.token_version을 더 크게 설정
    mocker.patch(
        "src.users.crud.get_user",
        return_value=user_models.User(id=payload["sub"], token_version=5),
    )
    mocker.patch("src.auth.crud.is_token_blocked", return_value=False)

    with pytest.raises(auth_exceptions.TokenExpiredError):
        await auth_deps._get_user_from_token(token=token, secret_key=secret, db=mock_db)


@pytest.mark.asyncio
async def test_get_current_user_from_refresh_token_sets_request_state(mocker):
    """get_current_user_from_refresh_token이 request.state.decoded_refresh_token_payload를 설정하는지 확인"""
    mock_db = AsyncMock()
    request = SimpleNamespace()
    request.state = SimpleNamespace()

    fake_user = user_models.User(id="u-refresh")
    fake_payload = {"sub": "u-refresh", "jti": "jti-refresh"}

    # 내부 _get_user_from_token을 패치하여 (user, payload)를 반환하도록 함
    mocker.patch(
        "src.auth.dependencies._get_user_from_token",
        return_value=(fake_user, fake_payload),
    )

    result = await auth_deps.get_current_user_from_refresh_token(
        request=request, token="t", db=mock_db
    )

    assert result is fake_user
    assert request.state.decoded_refresh_token_payload == fake_payload
