import pytest

from src.core import security


@pytest.mark.asyncio
async def test_hash_password():
    """
    비밀번호 해싱 테스트
    """
    # Arrange
    plain_password = "mysecretpassword"

    # Act
    hashed_password = security.hash_password(plain_password)

    # Assert
    assert hashed_password is not None
    assert hashed_password != plain_password
    assert security.verify_password(plain_password, hashed_password) is True


@pytest.mark.asyncio
async def test_verify_password():
    """
    비밀번호 검증 테스트
    """
    # Arrange
    plain_password = "mysecretpassword"
    hashed_password = security.hash_password(plain_password)

    # Act & Assert
    assert security.verify_password(plain_password, hashed_password) is True
    assert security.verify_password("wrongpassword", hashed_password) is False
