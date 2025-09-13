from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud
from src.core.security import hash_password
from src.users import crud as user_crud


@pytest.mark.asyncio
async def test_add_and_check_token_blocklist_integration(db_session: AsyncSession):
    """
    토큰 블락리스트 추가/확인 통합 테스트
    """
    # Arrange
    jti = "integration_test_jti"
    expires_at = datetime.now(timezone.utc)

    # Act - 토큰 블락리스트에 추가
    await crud.add_token_to_blocklist(
        db=db_session, jti=jti, expires_at=expires_at, user_id="test_user_id"
    )

    # Assert - 토큰이 블락리스트에 있는지 확인
    is_blocked = await crud.is_token_blocked(db=db_session, jti=jti)
    assert is_blocked is True

    # 없는 토큰은 블락되지 않음
    is_not_blocked = await crud.is_token_blocked(db=db_session, jti="nonexistent_jti")
    assert is_not_blocked is False


@pytest.mark.asyncio
async def test_invalidate_user_tokens(db_session: AsyncSession):
    """
    사용자의 모든 토큰 무효화 테스트
    """
    # Arrange - 사용자 생성
    user_email = "user_to_invalidate@example.com"
    user_in = user_crud.UserCreate(
        email=user_email,
        username="user_to_invalidate",
        password="password123!",
    )
    await user_crud.create_user(
        db=db_session,
        user_in=user_in,
        hashed_password=hash_password("password123!"),
    )
    db_user = await user_crud.get_user_by_email(db=db_session, email=user_email)
    assert db_user is not None
    assert db_user.token_version == 0  # 초기 토큰 버전은 0이어야 함

    user_id = str(db_user.id)

    # Act - 사용자 토큰 무효화
    await crud.invalidate_user_tokens(db=db_session, user_id=user_id)

    # Assert - 사용자 토큰 버전이 증가했는지 확인
    user = await user_crud.get_user(db=db_session, user_id=user_id)
    assert user is not None
    assert user.token_version == 1  # 초기값이 0이었다고 가정


@pytest.mark.asyncio
async def test_no_user_invalidate_user_tokens(db_session: AsyncSession):
    """
    존재하지 않는 사용자의 토큰 무효화 테스트
    """
    # Arrange - 존재하지 않는 사용자 ID
    non_existent_user_id = "nonexistent_user_id"

    # Act - 사용자 토큰 무효화 시도 (예외 발생하지 않아야 함)
    await crud.invalidate_user_tokens(db=db_session, user_id=non_existent_user_id)

    # Assert - 아무 일도 일어나지 않음 (예외가 발생하지 않음)


@pytest.mark.asyncio
async def test_cleanup_expired_tokens(db_session: AsyncSession):
    """
    만료된 토큰 정리 테스트
    """
    # Arrange - 만료된 토큰과 유효한 토큰 추가
    expired_jti = "expired_jti"
    valid_jti = "valid_jti"
    past_time = datetime(2000, 1, 1, tzinfo=timezone.utc)
    future_time = datetime(3000, 1, 1, tzinfo=timezone.utc)

    await crud.add_token_to_blocklist(
        db=db_session, jti=expired_jti, expires_at=past_time, user_id="user1"
    )
    await crud.add_token_to_blocklist(
        db=db_session, jti=valid_jti, expires_at=future_time, user_id="user2"
    )

    # Act - 만료된 토큰 정리
    await crud.cleanup_expired_tokens(db=db_session)

    # Assert - 만료된 토큰은 삭제되고 유효한 토큰은 남아있음
    is_expired_blocked = await crud.is_token_blocked(db=db_session, jti=expired_jti)
    is_valid_blocked = await crud.is_token_blocked(db=db_session, jti=valid_jti)

    assert is_expired_blocked is False  # 만료된 토큰은 삭제됨
    assert is_valid_blocked is True  # 유효한 토큰은 여전히 존재함
