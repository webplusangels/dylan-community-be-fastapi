import pytest
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users import crud
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdateProfile


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """
    사용자 생성 테스트
    """
    # Arrange
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    hashed_password = "hashed_password"

    # Act
    created_user = await crud.create_user(
        db=db_session, user_in=user_in, hashed_password=hashed_password
    )

    # Assert
    assert created_user.id is not None
    assert created_user.email == user_in.email
    assert created_user.username == user_in.username
    assert created_user.hashed_password == hashed_password
    assert created_user.profile_image_path is None
    assert created_user.is_active is True
    assert created_user.is_admin is False
    assert created_user.created_at is not None
    assert created_user.updated_at is not None
    assert created_user.created_at == created_user.updated_at


@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_session: AsyncSession, test_user: User):
    """
    중복 이메일로 사용자 생성 실패 테스트
    """
    # Arrange
    user_in = UserCreate(
        email=test_user.email,  # 이미 존재하는 이메일 사용
        username="newuser",
        password="newpassword123",
    )
    hashed_password = "hashed_password"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await crud.create_user(
            db=db_session, user_in=user_in, hashed_password=hashed_password
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_create_user_duplicate_username(
    db_session: AsyncSession, test_user: User
):
    """
    중복 사용자명으로 사용자 생성 실패 테스트
    """
    # Arrange
    user_in = UserCreate(
        email="test1@example.com",
        username=test_user.username,  # 이미 존재하는 사용자명 사용
        password="password123",
    )
    hashed_password = "hashed_password"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await crud.create_user(
            db=db_session, user_in=user_in, hashed_password=hashed_password
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession, test_user: User):
    """
    이메일로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user_by_email(db=db_session, email=test_user.email)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.email == test_user.email
    assert retrieved_user.username == test_user.username


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db_session: AsyncSession):
    """
    존재하지 않는 이메일로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user_by_email(
        db=db_session, email="nonexistent@example.com"
    )

    # Assert
    assert retrieved_user is None


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession, test_user: User):
    """
    사용자명으로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user_by_username(
        db=db_session, username=test_user.username
    )

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.email == test_user.email
    assert retrieved_user.username == test_user.username


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(db_session: AsyncSession):
    """
    존재하지 않는 사용자명으로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user_by_username(
        db=db_session, username="nonexistentuser"
    )

    # Assert
    assert retrieved_user is None


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession, test_user: User):
    """
    사용자 ID로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user(db=db_session, user_id=str(test_user.id))

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session: AsyncSession):
    """
    존재하지 않는 사용자 ID로 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user(db=db_session, user_id="nonexistent-id")

    # Assert
    assert retrieved_user is None


@pytest.mark.asyncio
async def test_get_users(db_session: AsyncSession):
    """
    사용자 목록 조회 테스트
    """
    # Arrange
    hashed_password = "hashed_password"
    test_users = []

    for i in range(5):
        user_in = UserCreate(
            email=f"gettest{i}@example.com",
            username=f"gettest{i}",
            password="password123",
        )
        created_user = await crud.create_user(
            db=db_session, user_in=user_in, hashed_password=hashed_password
        )
        test_users.append(created_user)

    # Act
    users = await crud.get_users(db=db_session, skip=0, limit=3)

    # Assert
    assert len(users) == 3
    # 최신 사용자부터 정렬되는지 확인
    for i in range(len(users) - 1):
        assert users[i].created_at >= users[i + 1].created_at


@pytest.mark.asyncio
async def test_get_users_pagination(db_session: AsyncSession):
    """
    사용자 목록 페이징 테스트
    """
    # Arrange
    hashed_password = "hashed_password"

    for i in range(5):
        user_in = UserCreate(
            email=f"pagetest{i}@example.com",
            username=f"pagetest{i}",
            password="password123",
        )
        await crud.create_user(
            db=db_session, user_in=user_in, hashed_password=hashed_password
        )

    # Act
    page1 = await crud.get_users(db=db_session, skip=0, limit=2)
    page2 = await crud.get_users(db=db_session, skip=2, limit=2)

    # Assert
    assert len(page1) == 2
    assert len(page2) == 2

    first_ids = {user.id for user in page1}
    second_ids = {user.id for user in page2}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.asyncio
async def test_update_user_success(db_session: AsyncSession, test_user: User):
    """
    사용자 정보 업데이트 테스트
    """
    # Arrange
    update_data = UserUpdateProfile(
        username="updated_username",
        profile_image_path="https://example.com/new_image.png",
    )

    # Act
    updated_user = await crud.update_user(
        db=db_session, db_user=test_user, user_update=update_data
    )

    # Assert
    assert updated_user.username == "updated_username"
    assert updated_user.profile_image_path == "https://example.com/new_image.png"


@pytest.mark.asyncio
async def test_update_user_no_changes(db_session: AsyncSession, test_user: User):
    """
    변경사항이 없는 사용자 업데이트 테스트
    """
    # Arrange
    original_updated_at = test_user.updated_at
    update_data = UserUpdateProfile(username=test_user.username)

    # Act
    updated_user = await crud.update_user(
        db=db_session, db_user=test_user, user_update=update_data
    )

    # Assert
    assert updated_user.username == test_user.username
    assert updated_user.updated_at == original_updated_at


@pytest.mark.asyncio
async def test_update_user_clear_profile_image(
    db_session: AsyncSession, test_user: User
):
    """
    프로필 이미지 삭제 테스트
    """
    # Arrange
    initial_update = UserUpdateProfile(
        profile_image_path="https://example.com/old_image.png"
    )
    await crud.update_user(db=db_session, db_user=test_user, user_update=initial_update)

    # 프로필 이미지가 설정되었는지 확인
    assert test_user.profile_image_path is not None

    # 새로운 업데이트 데이터 생성 (프로필 이미지 경로를 None으로 설정)
    update_data = UserUpdateProfile(
        username=test_user.username,  # 기존 값 유지
        profile_image_path=None,  # None으로 설정하여 삭제
    )
    # Act
    updated_user = await crud.update_user(
        db=db_session, db_user=test_user, user_update=update_data
    )

    # Assert
    assert updated_user.profile_image_path is None


@pytest.mark.asyncio
async def test_update_user_duplicate_username(db_session: AsyncSession):
    """
    중복 사용자명으로 업데이트 실패 테스트
    """
    # Arrange
    user1 = UserCreate(
        email="test1@example.com", username="user1", password="password123"
    )
    user2 = UserCreate(
        email="test2@example.com", username="user2", password="password123"
    )
    hashed_password = "hashed_password"

    created_user1 = await crud.create_user(
        db=db_session, user_in=user1, hashed_password=hashed_password
    )
    created_user2 = await crud.create_user(
        db=db_session, user_in=user2, hashed_password=hashed_password
    )

    # Act & Assert
    update_data = UserUpdateProfile(username=created_user1.username)
    with pytest.raises(HTTPException) as exc_info:
        await crud.update_user(
            db=db_session, db_user=created_user2, user_update=update_data
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_update_admin_status(db_session: AsyncSession, test_user: User):
    """
    관리자 상태 업데이트 테스트
    """
    # Arrange
    assert test_user.is_admin is False

    # Act
    updated_user = await crud.update_admin_status(
        db=db_session, db_user=test_user, is_admin=True
    )

    # Assert
    assert updated_user.is_admin is True


@pytest.mark.asyncio
async def test_update_admin_status_no_change(db_session: AsyncSession, test_user: User):
    """
    동일한 관리자 상태로 업데이트 테스트
    """
    # Act
    updated_user = await crud.update_admin_status(
        db=db_session, db_user=test_user, is_admin=test_user.is_admin
    )

    # Assert
    assert updated_user.is_admin == test_user.is_admin


@pytest.mark.asyncio
async def test_update_admin_status_failure(db_session: AsyncSession):
    """
    관리자 상태 업데이트 실패 테스트 (예외 발생)
    """
    # Arrange
    fake_user = User(id="nonexistent-id", is_active=True, deleted_at=None)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await crud.update_admin_status(db=db_session, db_user=fake_user, is_admin=True)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert (
        exc_info.value.detail
        == "사용자 관리자 상태 업데이트 중 데이터베이스 오류가 발생했습니다."
    )


@pytest.mark.asyncio
async def test_deactivate_user(db_session: AsyncSession, test_user: User):
    """
    사용자 비활성화 테스트
    """
    # Arrange
    assert test_user.is_active is True
    assert test_user.deleted_at is None

    # Act
    deactivated_user = await crud.deactivate_user(db=db_session, db_user=test_user)

    # Assert
    assert deactivated_user.is_active is False
    assert deactivated_user.deleted_at is not None


@pytest.mark.asyncio
async def test_deactivate_user_already_deactivated(
    db_session: AsyncSession, test_user: User
):
    """
    이미 비활성화된 사용자 재비활성화 테스트
    """
    # Arrange
    await crud.deactivate_user(db=db_session, db_user=test_user)
    original_deleted_at = test_user.deleted_at

    # Act
    deactivated_user = await crud.deactivate_user(db=db_session, db_user=test_user)

    # Assert
    assert deactivated_user.is_active is False
    assert deactivated_user.deleted_at == original_deleted_at


@pytest.mark.asyncio
async def test_deactivate_user_failure(db_session: AsyncSession):
    """
    사용자 비활성화 실패 테스트 (예외 발생)
    """
    # Arrange
    fake_user = User(id="nonexistent-id", is_active=True, deleted_at=None)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await crud.deactivate_user(db=db_session, db_user=fake_user)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert (
        exc_info.value.detail == "사용자 비활성화 중 데이터베이스 오류가 발생했습니다."
    )


@pytest.mark.asyncio
async def test_delete_user_success(db_session: AsyncSession, test_user: User):
    """
    사용자 삭제 테스트
    """
    # Arrange
    user_id = str(test_user.id)

    # Act
    result = await crud.delete_user(db=db_session, db_user=test_user)

    # Assert
    assert result is True

    # 삭제된 사용자가 데이터베이스에서 제거되었는지 확인
    stmt = select(User).where(User.id == user_id)
    db_result = await db_session.execute(stmt)
    deleted_user = db_result.scalar_one_or_none()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_user_failure(db_session: AsyncSession, mocker, test_user: User):
    """
    사용자 삭제 실패 테스트 (예외 발생)
    """
    # Arrange
    mocker.patch(
        "src.users.crud.delete_and_commit", side_effect=IntegrityError("", "", "")
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await crud.delete_user(db=db_session, db_user=test_user)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert (
        "사용자를 삭제할 수 없습니다. 관련된 데이터(게시글 등)가 존재합니다."
        in exc_info.value.detail
    )


@pytest.mark.asyncio
async def test_update_password(db_session: AsyncSession, test_user: User):
    """
    사용자 비밀번호 업데이트 테스트
    """
    # Arrange
    new_hashed_password = "new_hashed_password"
    original_password = test_user.hashed_password

    # Act
    updated_user = await crud.update_password(
        db=db_session, db_user=test_user, hashed_password=new_hashed_password
    )

    # Assert
    assert updated_user.hashed_password == new_hashed_password
    assert updated_user.hashed_password != original_password


@pytest.mark.asyncio
async def test_update_password_failure(db_session: AsyncSession):
    """
    사용자 비밀번호 업데이트 실패 테스트 (예외 발생)
    """
    # Arrange
    fake_user = User(id="nonexistent-id", is_active=True, deleted_at=None)
    new_hashed_password = "new_hashed_password"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await crud.update_password(
            db=db_session, db_user=fake_user, hashed_password=new_hashed_password
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert (
        exc_info.value.detail
        == "사용자 비밀번호 업데이트 중 데이터베이스 오류가 발생했습니다."
    )


@pytest.mark.asyncio
async def test_get_user_excludes_deactivated(db_session: AsyncSession, test_user: User):
    """
    비활성화된 사용자가 조회에서 제외되는지 테스트
    """
    # Arrange
    user_id = str(test_user.id)

    # Act
    await crud.deactivate_user(db=db_session, db_user=test_user)

    # Assert
    # 비활성화된 사용자는 조회되지 않아야 함
    retrieved_user = await crud.get_user(db=db_session, user_id=user_id)
    assert retrieved_user is None

    # 이메일로도 조회되지 않아야 함
    retrieved_by_email = await crud.get_user_by_email(
        db=db_session, email=test_user.email
    )
    assert retrieved_by_email is None

    # 사용자명으로도 조회되지 않아야 함
    retrieved_by_username = await crud.get_user_by_username(
        db=db_session, username=test_user.username
    )
    assert retrieved_by_username is None


@pytest.mark.asyncio
async def test_get_users_excludes_deactivated(db_session: AsyncSession):
    """
    비활성화된 사용자가 목록에서 제외되는지 테스트
    """
    # Arrange
    hashed_password = "hashed_password"

    # 활성 사용자 2명 생성
    active_user1 = await crud.create_user(
        db=db_session,
        user_in=UserCreate(
            email="active1@example.com", username="active1", password="password123"
        ),
        hashed_password=hashed_password,
    )
    active_user2 = await crud.create_user(
        db=db_session,
        user_in=UserCreate(
            email="active2@example.com", username="active2", password="password123"
        ),
        hashed_password=hashed_password,
    )

    # 비활성화할 사용자 1명 생성
    deactivated_user = await crud.create_user(
        db=db_session,
        user_in=UserCreate(
            email="deactivated@example.com",
            username="deactivated",
            password="password123",
        ),
        hashed_password=hashed_password,
    )

    # Act
    await crud.deactivate_user(db=db_session, db_user=deactivated_user)

    # Assert
    users = await crud.get_users(db=db_session, skip=0, limit=10)
    user_ids = [user.id for user in users]

    assert active_user1.id in user_ids
    assert active_user2.id in user_ids
    assert deactivated_user.id not in user_ids
    assert all(user.is_active is True for user in users)
