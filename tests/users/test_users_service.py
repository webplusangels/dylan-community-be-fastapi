from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status

from src.core.security import hash_password, verify_password
from src.users import models, schemas, service


@pytest.mark.asyncio
async def test_create_user_service_success(mocker):
    """
    사용자 생성 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    user_in = schemas.UserCreate(
        email="test@example.com", username="testuser", password="plainpassword123"
    )

    # Mocking
    created_user_mock = models.User(
        id="uuid", email=user_in.email, username=user_in.username
    )
    mock_crud_create = mocker.patch(
        "src.users.crud.create_user", return_value=created_user_mock
    )

    # Act
    result_user = await service.create_user(db=mock_db, user_in=user_in)

    # Assert
    mock_crud_create.assert_called_once()

    call_kwargs = mock_crud_create.call_args.kwargs
    assert call_kwargs["user_in"] == user_in
    assert "hashed_password" in call_kwargs
    assert verify_password(user_in.password, call_kwargs["hashed_password"])

    assert result_user.email == user_in.email


@pytest.mark.asyncio
async def test_update_user_profile_success(mocker):
    """
    사용자 프로필 업데이트 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    user_update = schemas.UserUpdate(
        username="updateduser",
        profile_image_path="https://example.com/updated_image.jpg",
    )
    db_user = models.User(
        username="testuser",
        profile_image_path="https://example.com/original_image.jpg",
    )
    updated_db_user = models.User(
        username="updateduser",
        profile_image_path="https://example.com/updated_image.jpg",
    )

    mock_crud_update = mocker.patch(
        "src.users.crud.update_user", return_value=updated_db_user
    )

    # Act
    updated_user = await service.update_user_profile(
        db=mock_db, db_user=db_user, user_update=user_update
    )

    # Assert
    mock_crud_update.assert_called_once_with(
        db=mock_db, db_user=db_user, user_update=user_update
    )
    assert updated_user.username == user_update.username
    assert updated_user.profile_image_path == str(user_update.profile_image_path)


@pytest.mark.asyncio
async def test_deactivate_user_success(mocker):
    """
    사용자 비활성화 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(is_active=True, is_admin=True)
    deactivated_user = models.User(is_active=False)

    mock_crud_deactivate = mocker.patch(
        "src.users.crud.deactivate_user", return_value=deactivated_user
    )

    # Act
    deactivated_user = await service.deactivate_user(db=mock_db, db_user=db_user)

    # Assert
    mock_crud_deactivate.assert_called_once_with(db=mock_db, db_user=db_user)
    assert not deactivated_user.is_active


@pytest.mark.asyncio
async def test_delete_user_success(mocker):
    """
    사용자 삭제 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(id="uuid", is_admin=True)
    mock_crud_delete_user = mocker.patch(
        "src.users.crud.delete_user", return_value=True
    )

    # Act
    await service.delete_user(db=mock_db, db_user=db_user)

    # Assert
    mock_crud_delete_user.assert_called_once_with(db=mock_db, db_user=db_user)


@pytest.mark.asyncio
async def test_update_admin_status_success(mocker):
    """
    관리자 상태 업데이트 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(id="1234", is_admin=True)
    updated_user = models.User(is_admin=False)
    current_user = models.User(id="515", is_admin=True)

    mocker.patch("src.users.crud.update_admin_status", return_value=updated_user)

    # Act
    updated_user = await service.update_admin_status(
        db=mock_db, db_user=db_user, is_admin=False, current_user=current_user
    )

    # Assert
    assert updated_user.is_admin is False


@pytest.mark.asyncio
async def test_update_admin_status_fail_self_deactivation():
    """
    관리자 상태 업데이트 실패 테스트 (자신의 관리자 권한 해제 시도)
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(id="1234", is_admin=True)
    current_user = models.User(id="1234", is_admin=True)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update_admin_status(
            db=mock_db, db_user=db_user, is_admin=False, current_user=current_user
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        exc_info.value.detail
        == "관리자는 자신의 관리자 권한을 해제할 수 없습니다."
        in exc_info.value.detail
    )

    assert db_user.is_admin is True  # 관리자 상태는 변경되지 않아야 함


@pytest.mark.asyncio
async def test_update_password_success(mocker):
    """
    사용자 비밀번호 업데이트 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    new_password = "newpassword123"
    db_user = models.User(hashed_password=hash_password("oldpassword123"))
    password_update = schemas.UserUpdatePassword(
        new_password=new_password, current_password="oldpassword123"
    )

    mock_crud_update_password = mocker.patch(
        "src.users.crud.update_password",
        return_value=models.User(id=db_user.id, hashed_password="new_hashed_password"),
    )

    # Act
    result = await service.update_password(
        db=mock_db, db_user=db_user, password_update=password_update
    )

    # Assert
    mock_crud_update_password.assert_called_once()
    call_kwargs = mock_crud_update_password.call_args.kwargs
    assert "hashed_password" in call_kwargs
    assert call_kwargs["hashed_password"] != new_password
    assert verify_password(new_password, call_kwargs["hashed_password"])
    assert result.hashed_password == "new_hashed_password"
