import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.crud import (
    create_like,
    delete_like,
    get_like,
    get_likes_by_post,
    get_likes_by_user,
    get_total_likes_count_by_post,
    get_total_likes_count_by_user,
)
from src.likes.schemas import PostLikeBase


@pytest.mark.asyncio
async def test_create_like(db_session: AsyncSession):
    """
    좋아요 생성 테스트
    """
    # Arrange
    like_in = PostLikeBase(post_id="p1", user_id="u1")

    # Act
    created_like = await create_like(db=db_session, like_in=like_in)

    # Assert
    assert created_like is not None
    assert created_like.post_id == like_in.post_id
    assert created_like.user_id == like_in.user_id


@pytest.mark.asyncio
async def test_create_like_fail(db_session: AsyncSession, mocker):
    """
    좋아요 생성 실패 테스트
    """
    # Arrange
    like_in = PostLikeBase(post_id="p1", user_id="u1")
    mocker.patch(
        "src.likes.crud.add_and_commit", side_effect=IntegrityError("", "", "")
    )

    # Act
    with pytest.raises(HTTPException) as exc_info:
        await create_like(db=db_session, like_in=like_in)

    # Assert
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "좋아요 생성 중 오류가 발생했습니다" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_like(db_session: AsyncSession):
    """
    특정 게시글과 사용자에 대한 좋아요 조회 테스트
    """
    # Arrange
    post_id = "p1"
    user_id = "u1"

    expected_like = PostLikeBase(post_id=post_id, user_id=user_id)

    # Act
    await create_like(db=db_session, like_in=expected_like)
    like = await get_like(db=db_session, post_id=post_id, user_id=user_id)

    # Assert
    assert like is not None
    assert like.post_id == post_id
    assert like.user_id == user_id


@pytest.mark.asyncio
async def test_get_likes_by_post(db_session: AsyncSession):
    """
    특정 게시글의 좋아요 목록 조회 테스트
    """
    # Arrange
    post_id = "p1"
    user_id = ["u1", "u2", "u3"]

    for uid in user_id:
        await create_like(
            db=db_session, like_in=PostLikeBase(post_id=post_id, user_id=uid)
        )

    # Act
    likes = await get_likes_by_post(db=db_session, post_id=post_id)

    # Assert
    assert likes is not None
    assert len(likes) == len(user_id)
    for like in likes:
        assert like.post_id == post_id
        assert like.user_id in user_id


@pytest.mark.asyncio
async def test_get_likes_by_user(db_session: AsyncSession):
    """
    특정 사용자의 좋아요 목록 조회 테스트
    """
    # Arrange
    post_id = ["p1", "p2", "p3"]
    user_id = "u1"

    for pid in post_id:
        await create_like(
            db=db_session, like_in=PostLikeBase(post_id=pid, user_id=user_id)
        )

    # Act
    likes = await get_likes_by_user(db=db_session, user_id=user_id)

    # Assert
    assert likes is not None
    assert len(likes) == len(post_id)
    for like in likes:
        assert like.post_id in post_id
        assert like.user_id == user_id


@pytest.mark.asyncio
async def test_get_total_likes_count_by_post(db_session: AsyncSession):
    """
    특정 게시글의 좋아요 총 개수 조회
    """
    # Arrange
    post_id = "p1"
    user_ids = ["u1", "u2", "u3"]

    for user_id in user_ids:
        await create_like(
            db=db_session, like_in=PostLikeBase(post_id=post_id, user_id=user_id)
        )

    # Act & Assert
    result = await get_total_likes_count_by_post(db=db_session, post_id=post_id)
    assert result == 3


@pytest.mark.asyncio
async def test_get_total_likes_count_by_user(db_session: AsyncSession):
    """
    특정 사용자의 좋아요 총 개수 조회
    """
    # Arrange
    user_id = "u1"
    post_ids = ["p1", "p2", "p3"]

    for post_id in post_ids:
        await create_like(
            db=db_session, like_in=PostLikeBase(post_id=post_id, user_id=user_id)
        )

    # Act & Assert
    result = await get_total_likes_count_by_user(db=db_session, user_id=user_id)
    assert result == 3


@pytest.mark.asyncio
async def test_delete_like(db_session: AsyncSession):
    """
    좋아요 삭제 테스트
    """
    # Arrange
    post_id = "p1"
    user_id = "u1"
    like_in = PostLikeBase(post_id=post_id, user_id=user_id)

    created_like = await create_like(db=db_session, like_in=like_in)

    # Act
    deleted_like = await delete_like(db=db_session, db_like=created_like)

    # Assert
    assert deleted_like is True


@pytest.mark.asyncio
async def test_delete_like_fail(db_session: AsyncSession, mocker):
    """
    좋아요 삭제 실패 테스트
    """
    # Arrange
    post_id = "p1"
    user_id = "u1"
    like_in = PostLikeBase(post_id=post_id, user_id=user_id)

    created_like = await create_like(db=db_session, like_in=like_in)
    mocker.patch(
        "src.likes.crud.delete_and_commit", side_effect=IntegrityError("", "", "")
    )

    # Act
    with pytest.raises(HTTPException) as exc_info:
        await delete_like(db=db_session, db_like=created_like)

    # Assert
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "좋아요 삭제 중 오류가 발생했습니다" in exc_info.value.detail
