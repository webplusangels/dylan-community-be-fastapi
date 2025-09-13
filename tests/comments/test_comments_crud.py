from datetime import datetime, timezone

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.comments import schemas
from src.comments.crud import (
    create_comment,
    deactivate_comment,
    delete_comment,
    get_comment,
    get_comments,
    get_total_comments_count,
    update_comment,
)


@pytest.mark.asyncio
async def test_create_and_get_comment_success(db_session: AsyncSession):
    """
    댓글 생성 및 조회 테스트
    """
    # Arrange
    comment_in = schemas.CommentCreate(
        post_id="post-id-123", content="This is a test comment."
    )

    # Act
    created_comment = await create_comment(
        db=db_session, comment_in=comment_in, user_id="user-id-123"
    )

    db_comment = await get_comment(db=db_session, comment_id=str(created_comment.id))

    # Assert
    assert db_comment is not None
    assert db_comment.id == created_comment.id
    assert db_comment.content == created_comment.content


@pytest.mark.asyncio
async def test_get_comments(db_session: AsyncSession):
    """
    특정 게시글의 댓글 목록 조회 테스트
    """
    # Arrange
    post_id = "post-id-123"
    comments_in = [
        schemas.CommentCreate(post_id=post_id, content="First comment"),
        schemas.CommentCreate(post_id=post_id, content="Second comment"),
        schemas.CommentCreate(post_id=post_id, content="Third comment"),
    ]

    for comment_in in comments_in:
        await create_comment(
            db=db_session, comment_in=comment_in, user_id="user-id-123"
        )

    # Act
    comments = await get_comments(db=db_session, post_id=post_id, skip=0, limit=10)

    # Assert
    assert len(comments) == 3
    assert comments[0].content == "Third comment"  # 최신 댓글이 먼저 나와야 함
    assert comments[1].content == "Second comment"
    assert comments[2].content == "First comment"


@pytest.mark.asyncio
async def test_get_total_comments_count(db_session: AsyncSession):
    """
    특정 게시글의 총 댓글 수 조회 테스트
    """
    # Arrange
    post_id = "post-id-123"
    comments_in = [
        schemas.CommentCreate(post_id=post_id, content="First comment"),
        schemas.CommentCreate(post_id=post_id, content="Second comment"),
        schemas.CommentCreate(post_id=post_id, content="Third comment"),
    ]

    for comment_in in comments_in:
        await create_comment(
            db=db_session, comment_in=comment_in, user_id="user-id-123"
        )

    # Act
    total_count = await get_total_comments_count(db=db_session, post_id=post_id)

    # Assert
    assert total_count == 3


@pytest.mark.asyncio
async def test_update_comment_success(db_session: AsyncSession):
    """
    댓글 수정 테스트
    """
    # Arrange
    comment_in = schemas.CommentCreate(
        post_id="post-id-123", content="This is a test comment."
    )
    created_comment = await create_comment(
        db=db_session, comment_in=comment_in, user_id="user-id-123"
    )

    update_data = schemas.CommentUpdate(content="Updated comment content")

    # Act
    db_comment = await get_comment(db=db_session, comment_id=str(created_comment.id))
    db_comment.content = update_data.content
    db_comment.updated_at = datetime.now(timezone.utc)
    await db_session.commit()
    await db_session.refresh(db_comment)

    # Assert
    assert db_comment.content == "Updated comment content"


@pytest.mark.asyncio
async def test_update_deleted_comment_fail(db_session: AsyncSession, mocker):
    """
    댓글 삭제 성공 및 수정 실패 테스트 (예외 발생)
    """
    # Arrange
    comment_in = schemas.CommentCreate(
        post_id="post-id-123", content="This is a test comment."
    )
    db_comment = await create_comment(
        db=db_session, comment_in=comment_in, user_id="user-id-123"
    )

    # Act & Assert
    deactivated_comment = await deactivate_comment(db=db_session, db_comment=db_comment)

    assert deactivated_comment.is_active is False

    mocker.patch(
        "src.comments.crud.commit_and_refresh", side_effect=IntegrityError("", "", "")
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_comment(
            db=db_session,
            db_comment=deactivated_comment,
            comment_update=schemas.CommentUpdate(content="New content"),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "댓글 업데이트 중 오류가 발생했습니다" in exc_info.value.detail


@pytest.mark.asyncio
async def test_deactivate_comment_fail(db_session: AsyncSession, mocker):
    """
    이미 삭제된 댓글 비활성화 실패 테스트
    """
    # Arrange
    comment_in = schemas.CommentCreate(
        post_id="post-id-123", content="This is a test comment."
    )
    db_comment = await create_comment(
        db=db_session, comment_in=comment_in, user_id="user-id-123"
    )

    mocker.patch(
        "src.comments.crud.commit_and_refresh", side_effect=IntegrityError("", "", "")
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await deactivate_comment(db=db_session, db_comment=db_comment)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "댓글 비활성화 중 오류가 발생했습니다" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_comment_success(db_session: AsyncSession):
    """
    댓글 영구 삭제 테스트
    """
    # Arrange
    comment_in = schemas.CommentCreate(
        post_id="post-id-123", content="This is a test comment."
    )
    db_comment = await create_comment(
        db=db_session, comment_in=comment_in, user_id="user-id-123"
    )

    # Act
    result = await delete_comment(db=db_session, db_comment=db_comment)

    # Assert
    assert result is True

    deleted_comment = await get_comment(db=db_session, comment_id=str(db_comment.id))
    assert deleted_comment is None


@pytest.mark.asyncio
async def test_delete_comment_fail(db_session: AsyncSession, mocker):
    """
    댓글 영구 삭제 실패 테스트 (예외 발생)
    """
    # Arrange
    comment_in = schemas.CommentCreate(
        post_id="post-id-123", content="This is a test comment."
    )
    db_comment = await create_comment(
        db=db_session, comment_in=comment_in, user_id="user-id-123"
    )

    mocker.patch(
        "src.comments.crud.delete_and_commit", side_effect=IntegrityError("", "", "")
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await delete_comment(db=db_session, db_comment=db_comment)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "댓글 삭제 중 오류가 발생했습니다" in exc_info.value.detail
