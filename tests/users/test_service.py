from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

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
async def test_create_user_service_failure_duplicate_email(mocker):
    """
    사용자 생성 서비스 로직 실패 테스트(중복 이메일)
    """
    # Arrange
    mock_db = AsyncMock()
    user_in = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="plainpassword123",
    )

    # Mocking
    mocker.patch(
        "src.users.crud.create_user",
        side_effect=HTTPException(
            status_code=409, detail="이미 사용 중인 이메일 또는 사용자 이름입니다."
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.create_user(db=mock_db, user_in=user_in)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "이미 사용 중인 이메일 또는 사용자 이름입니다."


@pytest.mark.asyncio
async def test_create_user_service_failure_duplicate_username(mocker):
    """
    사용자 생성 서비스 로직 실패 테스트(중복 사용자 이름)
    """
    # Arrange
    mock_db = AsyncMock()
    user_in = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="plainpassword123",
    )

    # Mocking
    mocker.patch(
        "src.users.crud.create_user",
        side_effect=HTTPException(
            status_code=409, detail="이미 사용 중인 이메일 또는 사용자 이름입니다."
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.create_user(db=mock_db, user_in=user_in)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "이미 사용 중인 이메일 또는 사용자 이름입니다."


@pytest.mark.asyncio
async def test_authenticate_user_success(mocker):
    """
    사용자 인증 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    test_user = models.User(
        email="test@example.com",
        is_active=True,
    )

    mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
    mocker.patch("src.users.service.verify_password", return_value=True)

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
    test_user = models.User(
        email="test@example.com",
        hashed_password=hash_password("plainpassword123"),
        is_active=True,
    )

    mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
    mocker.patch("src.users.service.verify_password", return_value=False)

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
    test_user = models.User(
        email="test@example.com",
        hashed_password=hash_password("plainpassword123"),
        is_active=False,  # 비활성화된 사용자
    )

    mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
    mocker.patch("src.users.service.verify_password", return_value=True)

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
    test_user = models.User(
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
async def test_get_user_profile_success(mocker):
    """
    사용자 프로필 조회 성공 테스트
    """
    # Arrange
    test_user = models.User(
        id="uuid",
    )

    mocker.patch("src.users.crud.get_user", return_value=test_user)

    # Act
    user_profile = await service.get_user_profile(db_user=test_user)

    # Assert
    assert user_profile is not None
    assert user_profile.id == test_user.id


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
async def test_update_user_failure_duplicate_username(mocker):
    """
    사용자 이름 중복으로 인한 업데이트 실패 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    user_update = schemas.UserUpdate(username="duplicateuser")
    db_user = models.User(username="testuser")

    mocker.patch(
        "src.users.crud.update_user",
        side_effect=HTTPException(
            status_code=409, detail="이미 사용 중인 이메일 또는 사용자 이름입니다."
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user_profile(
            db=mock_db, db_user=db_user, user_update=user_update
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "이미 사용 중인 이메일 또는 사용자 이름입니다."


@pytest.mark.asyncio
async def test_deactivate_user_success(mocker):
    """
    사용자 비활성화 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(is_active=True)
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
async def test_deactivate_user_failure(mocker):
    """
    사용자 비활성화 실패 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(is_active=True)
    mocker.patch(
        "src.users.crud.deactivate_user",
        side_effect=HTTPException(
            status_code=500, detail="사용자 비활성화 중 오류가 발생했습니다."
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.deactivate_user(db=mock_db, db_user=db_user)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "사용자 비활성화 중 오류가 발생했습니다."


@pytest.mark.asyncio
async def test_delete_user_success(mocker):
    """
    사용자 삭제 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(id="uuid")
    mock_crud_delete_user = mocker.patch(
        "src.users.crud.delete_user", return_value=True
    )

    # Act
    await service.delete_user(db=mock_db, db_user=db_user)

    # Assert
    mock_crud_delete_user.assert_called_once_with(db=mock_db, db_user=db_user)


@pytest.mark.asyncio
async def test_delete_user_failure(mocker):
    """
    사용자 삭제 실패 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(id="uuid")
    mocker.patch(
        "src.users.crud.delete_user",
        side_effect=HTTPException(
            status_code=409,
            detail="사용자를 삭제할 수 없습니다. 관련된 데이터가 존재합니다.",
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_user(db=mock_db, db_user=db_user)

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail
        == "사용자를 삭제할 수 없습니다. 관련된 데이터가 존재합니다."
    )


@pytest.mark.asyncio
async def test_update_admin_status_success(mocker):
    """
    관리자 상태 업데이트 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(is_admin=True)
    updated_user = models.User(is_admin=False)

    mocker.patch("src.users.crud.update_admin_status", return_value=updated_user)

    # Act
    updated_user = await service.update_admin_status(
        db=mock_db, db_user=db_user, is_admin=False
    )

    # Assert
    assert updated_user.is_admin is False


@pytest.mark.asyncio
async def test_update_admin_status_failure(mocker):
    """
    관리자 상태 업데이트 실패 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(is_admin=True)

    mocker.patch(
        "src.users.crud.update_admin_status",
        side_effect=HTTPException(
            status_code=500, detail="관리자 상태 업데이트 중 오류가 발생했습니다."
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update_admin_status(db=mock_db, db_user=db_user, is_admin=False)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "관리자 상태 업데이트 중 오류가 발생했습니다."


@pytest.mark.asyncio
async def test_update_password_success(mocker):
    """
    사용자 비밀번호 업데이트 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    new_password = "newpassword123"
    db_user = models.User(hashed_password=hash_password("oldpassword123"))
    updated_user = models.User(hashed_password="new_hashed_password")

    mock_crud_update_password = mocker.patch(
        "src.users.crud.update_password", return_value=updated_user
    )

    # Act
    result = await service.update_password(
        db=mock_db, db_user=db_user, new_password=new_password
    )

    # Assert
    mock_crud_update_password.assert_called_once()
    call_kwargs = mock_crud_update_password.call_args.kwargs
    assert "hashed_password" in call_kwargs
    assert call_kwargs["hashed_password"] != new_password
    assert verify_password(new_password, call_kwargs["hashed_password"])
    assert result.hashed_password == "new_hashed_password"


@pytest.mark.asyncio
async def test_update_password_failure(mocker):
    """
    사용자 비밀번호 업데이트 실패 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_user = models.User(hashed_password=hash_password("oldpassword123"))

    mocker.patch(
        "src.users.crud.update_password",
        side_effect=HTTPException(
            status_code=500,
            detail="사용자 비밀번호 업데이트 중 서버 오류가 발생했습니다.",
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update_password(
            db=mock_db, db_user=db_user, new_password="newpassword123"
        )

    assert exc_info.value.status_code == 500
    assert (
        exc_info.value.detail == "사용자 비밀번호 업데이트 중 서버 오류가 발생했습니다."
    )
