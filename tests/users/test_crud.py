import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.users import crud
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate


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
async def test_create_user_duplicate_email(
    db_session: AsyncSession, user_fixture: User
):
    """
    중복 이메일로 사용자 생성 테스트
    """
    # Arrange
    user_in = UserCreate(
        email=user_fixture.email,  # 이미 존재하는 이메일 사용
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
    db_session: AsyncSession, user_fixture: User
):
    """
    중복 사용자 이름으로 사용자 생성 테스트
    """
    # Arrange
    user_in = UserCreate(
        email="test1@example.com",
        username=user_fixture.username,  # 이미 존재하는 사용자 이름 사용
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
async def test_get_user_by_email(db_session: AsyncSession, user_fixture: User):
    """
    이메일로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user_by_email(
        db=db_session, email=user_fixture.email
    )

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == user_fixture.id
    assert retrieved_user.email == user_fixture.email
    assert retrieved_user.username == user_fixture.username
    assert retrieved_user.hashed_password == user_fixture.hashed_password
    assert retrieved_user.profile_image_path == user_fixture.profile_image_path
    assert retrieved_user.created_at == user_fixture.created_at
    assert retrieved_user.updated_at == user_fixture.updated_at


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db_session: AsyncSession):
    """
    존재하지 않는 이메일로 사용자 조회 테스트
    """
    # Act
    non_existing_user = await crud.get_user_by_email(
        db=db_session, email="nonexistent@example.com"
    )

    # Assert
    assert non_existing_user is None


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession, user_fixture: User):
    """
    사용자 이름으로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user_by_username(
        db=db_session, username=user_fixture.username
    )

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == user_fixture.id
    assert retrieved_user.email == user_fixture.email
    assert retrieved_user.username == user_fixture.username


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(db_session: AsyncSession):
    """
    존재하지 않는 사용자 이름으로 사용자 조회 테스트
    """
    # Act
    non_existing_user = await crud.get_user_by_username(
        db=db_session, username="nonexistentuser"
    )

    # Assert
    assert non_existing_user is None


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession, user_fixture: User):
    """
    사용자 ID로 사용자 조회 테스트
    """
    # Act
    retrieved_user = await crud.get_user(db=db_session, user_id=user_fixture.id)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == user_fixture.id
    assert retrieved_user.email == user_fixture.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session: AsyncSession):
    """
    존재하지 않는 사용자 ID로 조회 테스트
    """
    # Act
    non_existing_user = await crud.get_user(db=db_session, user_id="nonexistent-id")

    # Assert
    assert non_existing_user is None


@pytest.mark.asyncio
async def test_get_users(db_session: AsyncSession):
    """
    사용자 목록 조회 테스트 (기본 케이스 + 페이징)
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
        created = await crud.create_user(
            db=db_session, user_in=user_in, hashed_password=hashed_password
        )
        test_users.append(created)

    # Act & Assert - 전체 조회
    all_users = await crud.get_users(db=db_session)
    assert len(all_users) >= 5
    assert all(user.id in [u.id for u in test_users] for user in all_users)

    # Act & Assert - 페이징
    page1 = await crud.get_users(db=db_session, skip=0, limit=2)
    page2 = await crud.get_users(db=db_session, skip=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2

    first_ids = {user.id for user in page1}
    second_ids = {user.id for user in page2}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.asyncio
async def test_update_user_success(db_session: AsyncSession, user_fixture: User):
    """
    사용자 정상 업데이트 테스트
    """
    # Arrange
    update = UserUpdate(
        username="testuser_updated", profile_image_path="https://example.com/img.png"
    )

    # Act
    updated = await crud.update_user(
        db=db_session, db_user=user_fixture, user_update=update
    )

    # Assert
    assert updated.username == "testuser_updated"
    assert updated.profile_image_path == "https://example.com/img.png"
    assert type(updated.profile_image_path) is str

    # profile_image_path가 None인 경우 업데이트 테스트
    # Arrange 2
    update_2 = UserUpdate(profile_image_path=None)

    # Act 2
    updated_2 = await crud.update_user(
        db=db_session, db_user=updated, user_update=update_2
    )

    # Assert 2
    assert updated_2.profile_image_path is None


@pytest.mark.asyncio
async def test_update_user_duplicate_username(db_session: AsyncSession):
    """
    중복 사용자 이름으로 사용자 업데이트 테스트
    """
    # Arrange
    user1 = UserCreate(
        email="test1@example.com", username="user1", password="password123"
    )
    user2 = UserCreate(
        email="test2@example.com", username="user2", password="password123"
    )
    hashed_password = "hashed_password"

    await crud.create_user(
        db=db_session, user_in=user1, hashed_password=hashed_password
    )
    created2 = await crud.create_user(
        db=db_session, user_in=user2, hashed_password=hashed_password
    )

    # Act & Assert
    update = UserUpdate(username="user1")
    with pytest.raises(HTTPException) as exc_info:
        await crud.update_user(db=db_session, db_user=created2, user_update=update)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_update_admin_status(db_session: AsyncSession, user_fixture: User):
    """
    관리자 상태 업데이트 테스트
    """
    # Act
    updated = await crud.update_admin_status(
        db=db_session, db_user=user_fixture, is_admin=True
    )

    # Assert
    assert updated.is_admin is True


@pytest.mark.asyncio
async def test_deactivate_user(db_session: AsyncSession, user_fixture: User):
    """
    사용자 비활성화 테스트
    """
    # Act
    deactivated = await crud.deactivate_user(db=db_session, db_user=user_fixture)

    # Assert
    assert deactivated.is_active is False


@pytest.mark.asyncio
async def test_delete_user_success(db_session: AsyncSession, user_fixture: User):
    """
    사용자 삭제 테스트
    """
    # Act
    result = await crud.delete_user(db=db_session, db_user=user_fixture)

    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_update_password(db_session: AsyncSession, user_fixture: User):
    """
    사용자 비밀번호 업데이트 테스트
    """
    # Act
    new_hashed = "newhashedpassword"
    updated = await crud.update_password(
        db=db_session, db_user=user_fixture, hashed_password=new_hashed
    )

    # Assert
    assert updated.hashed_password == new_hashed
