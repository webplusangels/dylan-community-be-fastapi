from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.posts import models, schemas, service
from src.users.models import User


@pytest.mark.asyncio
async def test_create_post_service_success(mocker):
    """
    게시글 생성 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    post_create = schemas.PostCreate(
        title="Test Post", content="This is a test post content."
    )
    db_user = User(id="user-id-123", email="test@example.com", username="testuser")

    created_post_mock = models.Post(
        id="post-id-123",
        title=post_create.title,
        content=post_create.content,
        user_id=db_user.id,
    )
    mock_crud_create_post = mocker.patch(
        "src.posts.crud.create_post", return_value=created_post_mock
    )

    # Act
    result_post = await service.create_post(
        db=mock_db, post_create=post_create, db_user=db_user
    )

    # Assert
    mock_crud_create_post.assert_called_once_with(
        db=mock_db, post_in=post_create, user_id=db_user.id
    )
    assert result_post.title == post_create.title
    assert result_post.content == post_create.content
    assert result_post.user_id == db_user.id


@pytest.mark.asyncio
async def test_create_post_service_failure(mocker):
    """
    게시글 생성 서비스 로직 실패 테스트 (예외 발생)
    """
    # Arrange
    mock_db = AsyncMock()
    post_create = schemas.PostCreate(
        title="Test Post", content="This is a test post content."
    )
    db_user = User(id="user-id-123")

    mock_crud_create_post = mocker.patch(
        "src.posts.crud.create_post",
        side_effect=HTTPException(
            status_code=409,
            detail="게시글 생성 중 오류가 발생했습니다. 존재하지 않는 사용자 ID이거나 리소스 충돌이 발생했을 수 있습니다.",
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.create_post(db=mock_db, post_create=post_create, db_user=db_user)
    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail
        == "게시글 생성 중 오류가 발생했습니다. 존재하지 않는 사용자 ID이거나 리소스 충돌이 발생했을 수 있습니다."
    )
    mock_crud_create_post.assert_called_once_with(
        db=mock_db, post_in=post_create, user_id=db_user.id
    )


@pytest.mark.asyncio
async def test_get_post_by_id_service_success(mocker):
    """
    게시글 ID로 조회 서비스 로직 성공 테스트 (조회수 증가 포함)
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(
        id="post-id-123", title="Existing Post", content="Content", views=0
    )

    mock_crud_increment_views = mocker.patch(
        "src.posts.crud.increment_post_views", return_value=None
    )
    mock_db_refresh = mocker.patch.object(mock_db, "refresh", return_value=None)

    # Act
    result_post = await service.get_post_by_id(db=mock_db, db_post=db_post)

    # Assert
    mock_crud_increment_views.assert_called_once_with(db=mock_db, db_post=db_post)
    mock_db_refresh.assert_called_once_with(db_post)
    assert result_post == db_post


@pytest.mark.asyncio
async def test_get_posts_with_total_count_service_success(mocker):
    """
    게시글 목록 조회 및 총 개수 반환 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    posts_mock = [
        models.Post(id="p1", title="Post 1", content="c1"),
        models.Post(id="p2", title="Post 2", content="c2"),
    ]
    total_count_mock = 2

    mock_crud_get_posts = mocker.patch(
        "src.posts.crud.get_posts", return_value=posts_mock
    )
    mock_crud_get_total_post_count = mocker.patch(
        "src.posts.crud.get_total_post_count", return_value=total_count_mock
    )

    # Act
    result_posts, result_total_count = await service.get_posts_with_total_count(
        db=mock_db, skip=0, limit=10
    )

    # Assert
    mock_crud_get_posts.assert_called_once_with(db=mock_db, skip=0, limit=10)
    mock_crud_get_total_post_count.assert_called_once_with(db=mock_db)
    assert result_posts == posts_mock
    assert result_total_count == total_count_mock


@pytest.mark.asyncio
async def test_update_post_service_success(mocker):
    """
    게시글 업데이트 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(
        id="post-id-123", title="Original", content="Original Content"
    )
    post_update = schemas.PostUpdate(title="Updated Title", content="Updated Content")

    updated_post_mock = models.Post(
        id="post-id-123", title="Updated Title", content="Updated Content"
    )
    mock_crud_update_post = mocker.patch(
        "src.posts.crud.update_post", return_value=updated_post_mock
    )

    # Act
    result_post = await service.update_post(
        db=mock_db, db_post=db_post, post_update=post_update
    )

    # Assert
    mock_crud_update_post.assert_called_once_with(
        db=mock_db, db_post=db_post, post_update=post_update
    )
    assert result_post.title == post_update.title
    assert result_post.content == post_update.content


@pytest.mark.asyncio
async def test_update_post_service_failure(mocker):
    """
    게시글 업데이트 서비스 로직 실패 테스트 (예외 발생)
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(
        id="post-id-123", title="Original", content="Original Content"
    )
    post_update = schemas.PostUpdate(title="Updated Title", content="Updated Content")

    mock_crud_update_post = mocker.patch(
        "src.posts.crud.update_post",
        side_effect=HTTPException(
            status_code=409,
            detail="게시글 업데이트 중 오류가 발생했습니다. 리소스 충돌이 발생했을 수 있습니다.",
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update_post(db=mock_db, db_post=db_post, post_update=post_update)

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail
        == "게시글 업데이트 중 오류가 발생했습니다. 리소스 충돌이 발생했을 수 있습니다."
    )
    mock_crud_update_post.assert_called_once_with(
        db=mock_db, db_post=db_post, post_update=post_update
    )


@pytest.mark.asyncio
async def test_deactivate_post_service_success(mocker):
    """
    게시글 비활성화 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(id="post-id-123", is_active=True)

    deactivated_post_mock = models.Post(id="post-id-123", is_active=False)
    mock_crud_deactivate_post = mocker.patch(
        "src.posts.crud.deactivate_post", return_value=deactivated_post_mock
    )

    # Act
    result_post = await service.deactivate_post(db=mock_db, db_post=db_post)

    # Assert
    mock_crud_deactivate_post.assert_called_once_with(db=mock_db, db_post=db_post)
    assert result_post.is_active is False


@pytest.mark.asyncio
async def test_deactivate_post_service_failure(mocker):
    """
    게시글 비활성화 서비스 로직 실패 테스트 (예외 발생)
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(id="post-id-123", is_active=True)

    mock_crud_deactivate_post = mocker.patch(
        "src.posts.crud.deactivate_post",
        side_effect=HTTPException(
            status_code=409,
            detail="게시글 비활성화 중 오류가 발생했습니다. 리소스 충돌이 발생했을 수 있습니다.",
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.deactivate_post(db=mock_db, db_post=db_post)

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail
        == "게시글 비활성화 중 오류가 발생했습니다. 리소스 충돌이 발생했을 수 있습니다."
    )
    mock_crud_deactivate_post.assert_called_once_with(db=mock_db, db_post=db_post)


@pytest.mark.asyncio
async def test_delete_post_service_success(mocker):
    """
    게시글 삭제 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(id="post-id-123")

    mock_crud_delete_post = mocker.patch(
        "src.posts.crud.delete_post", return_value=None
    )

    # Act
    result = await service.delete_post(db=mock_db, db_post=db_post)

    # Assert
    mock_crud_delete_post.assert_called_once_with(db=mock_db, db_post=db_post)
    assert result is None


@pytest.mark.asyncio
async def test_delete_post_service_failure(mocker):
    """
    게시글 삭제 서비스 로직 실패 테스트 (예외 발생)
    """
    # Arrange
    mock_db = AsyncMock()
    db_post = models.Post(id="post-id-123")

    mock_crud_delete_post = mocker.patch(
        "src.posts.crud.delete_post",
        side_effect=HTTPException(
            status_code=409,
            detail="게시글 삭제 중 오류가 발생했습니다.",
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_post(db=mock_db, db_post=db_post)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "게시글 삭제 중 오류가 발생했습니다."
    mock_crud_delete_post.assert_called_once_with(db=mock_db, db_post=db_post)


@pytest.mark.asyncio
async def test_search_posts_service_success(mocker):
    """
    게시글 검색 서비스 로직 성공 테스트
    """
    # Arrange
    mock_db = AsyncMock()
    query = "test"
    skip = 0
    limit = 5
    posts_mock = [
        models.Post(id="p1", title="Test Post 1", content="Content 1"),
        models.Post(id="p2", title="Test Post 2", content="Content 2"),
    ]

    mock_crud_search_posts = mocker.patch(
        "src.posts.crud.search_posts", return_value=posts_mock
    )

    # Act
    result_posts = await service.search_posts(
        db=mock_db, query=query, skip=skip, limit=limit
    )

    # Assert
    mock_crud_search_posts.assert_called_once_with(
        db=mock_db, query=query, skip=skip, limit=limit
    )
    assert result_posts == posts_mock
