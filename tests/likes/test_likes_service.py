from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status

from src.likes import models, service
from src.users.models import User


@pytest.mark.asyncio
async def test_create_like(mocker):
    # Arrange
    mock_db = AsyncMock()
    db_user = User(id="u1")
    post_id = "p1"

    mocker.patch("src.likes.crud.get_like", return_value=None)

    mocker.patch(
        "src.likes.crud.create_like",
        return_value=models.PostLike(post_id=post_id, user_id=db_user.id),
    )

    # Act
    like = await service.create_like(db=mock_db, post_id=post_id, db_user=db_user)

    # Assert
    assert like.post_id == post_id
    assert like.user_id == db_user.id


@pytest.mark.asyncio
async def test_create_like_conflict(mocker):
    # Arrange
    mock_db = AsyncMock()
    db_user = User(id="u1")
    post_id = "p1"

    mocker.patch(
        "src.likes.crud.get_like",
        return_value=models.PostLike(post_id=post_id, user_id=db_user.id),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.create_like(db=mock_db, post_id=post_id, db_user=db_user)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "이미 좋아요를 누른 게시글입니다." in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_like_by_post_and_user(mocker):
    # Arrange
    mock_db = AsyncMock()
    db_user = User(id="u1")
    post_id = "p1"

    expected_like = models.PostLike(post_id=post_id, user_id=db_user.id)
    mocker.patch("src.likes.crud.get_like", return_value=expected_like)

    # Act
    like = await service.get_like_by_post_and_user(
        db=mock_db, post_id=post_id, user_id=db_user.id
    )

    # Assert
    assert like == expected_like


@pytest.mark.asyncio
async def test_get_likes_with_total_count_by_post(mocker):
    mock_db = AsyncMock()

    likes = [models.PostLike(post_id="p1", user_id="u1")]
    total_count = 1

    mocker.patch("src.likes.crud.get_likes_by_post", return_value=likes)
    mocker.patch(
        "src.likes.crud.get_total_likes_count_by_post", return_value=total_count
    )

    result_likes, result_total = await service.get_likes_with_total_count_by_post(
        db=mock_db, post_id="p1", skip=0, limit=10
    )

    assert result_likes == likes
    assert result_total == total_count


@pytest.mark.asyncio
async def test_get_likes_with_total_count_by_user(mocker):
    mock_db = AsyncMock()

    likes = [models.PostLike(post_id="p1", user_id="u1")]
    total_count = 1

    mocker.patch("src.likes.crud.get_likes_by_user", return_value=likes)
    mocker.patch(
        "src.likes.crud.get_total_likes_count_by_user", return_value=total_count
    )

    result_likes, result_total = await service.get_likes_with_total_count_by_user(
        db=mock_db, user_id="u1", skip=0, limit=10
    )

    assert result_likes == likes
    assert result_total == total_count


@pytest.mark.asyncio
async def test_toggle_like_add_and_remove(mocker):
    # Arrange
    mock_db = AsyncMock()
    db_user = User(id="u1")
    post_id = "p1"
    like_model = models.PostLike(post_id=post_id, user_id=db_user.id)

    mocker.patch("src.likes.crud.get_like", return_value=None)
    mocker.patch("src.likes.crud.create_like", return_value=like_model)

    # Act - Like 추가
    like, action_add = await service.toggle_like(
        db=mock_db, post_id=post_id, db_user=db_user
    )

    # Assert - Like 추가
    assert like.post_id == post_id
    assert like.user_id == db_user.id
    assert action_add is True

    # Arrange - Like가 이미 존재하는 상태로 변경
    mocker.patch(
        "src.likes.crud.get_like",
        return_value=like_model,
    )
    mocker.patch("src.likes.crud.delete_like", return_value=None)

    # Act - Like 제거
    removed, action_remove = await service.toggle_like(
        db=mock_db, post_id=post_id, db_user=db_user
    )

    # Assert - Like 제거
    assert removed is None
    assert action_remove is False
