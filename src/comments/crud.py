from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.comments.models import PostComment
from src.comments.schemas import CommentCreate, CommentUpdate
from src.common.crud import add_and_commit, commit_and_refresh, delete_and_commit


async def create_comment(
    db: AsyncSession, comment_in: CommentCreate, user_id: str
) -> PostComment:
    """
    새로운 댓글을 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param comment_in: 댓글 생성 스키마
    :param user_id: 댓글 작성자의 사용자 ID
    :return: 생성된 댓글 모델
    """
    db_comment = PostComment(
        **comment_in.model_dump(),
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
    )
    await add_and_commit(db, db_comment)
    return db_comment


async def get_comment(db: AsyncSession, comment_id: str) -> PostComment | None:
    """
    댓글을 ID로 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param comment_id: 조회할 댓글 ID
    :return: 댓글 모델 또는 None
    """
    # Eager-load the author to avoid triggering lazy async IO during
    # response serialization (Pydantic will access `author` attribute).
    stmt = PostComment.with_author(PostComment.active_query()).where(
        PostComment.id == comment_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_comments(
    db: AsyncSession, post_id: str, skip: int = 0, limit: int = 10
) -> Sequence[PostComment]:
    """
    게시글에 대한 댓글 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 댓글이 속한 게시글 ID
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 댓글 수 (페이징)
    :return: 댓글 모델 리스트
    """
    # Eager-load authors for the comments list to avoid lazy-loading in sync
    # during response serialization.
    stmt = (
        PostComment.with_author(PostComment.active_query())
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_total_comments_count(db: AsyncSession, post_id: str) -> int:
    """
    게시글에 대한 총 댓글 수를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 댓글이 속한 게시글 ID
    :return: 총 댓글 수
    """
    stmt = (
        PostComment.active_query()
        .where(PostComment.post_id == post_id)
        .with_only_columns(func.count(PostComment.id))
    )
    result = await db.execute(stmt)
    return result.scalar_one() or 0


async def update_comment(
    db: AsyncSession, db_comment: PostComment, comment_update: CommentUpdate
) -> PostComment:
    """
    댓글을 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 데이터베이스에서 조회된 댓글 모델
    :param comment_update: 댓글 업데이트 스키마
    :return: 업데이트된 댓글 모델
    :raises HTTPException: 댓글 업데이트 중 오류가 발생한 경우
    """
    update_data = comment_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_comment, key, value)

    try:
        return await commit_and_refresh(db, db_comment)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"댓글 업데이트 중 오류가 발생했습니다: {err.orig}",
        ) from err


async def deactivate_comment(db: AsyncSession, db_comment: PostComment) -> PostComment:
    """
    댓글을 비활성화(삭제)합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 비활성화할 댓글 모델 (DB에서 조회된 상태여야 함)
    :return: 비활성화된 댓글 모델
    :raises HTTPException: 댓글 비활성화 중 오류가 발생한 경우
    """
    if db_comment.deleted_at is None:
        db_comment.deleted_at = datetime.now(timezone.utc)
        db_comment.is_active = False

        try:
            await commit_and_refresh(db, db_comment)
            return db_comment
        except IntegrityError as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"댓글 비활성화 중 오류가 발생했습니다: {err.orig}",
            ) from err


async def delete_comment(db: AsyncSession, db_comment: PostComment) -> bool:
    """
    댓글을 영구 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 삭제할 댓글 모델 (DB에서 조회된 상태여야 함)
    :return: 삭제 성공 여부 (True)
    :raises HTTPException: 댓글 삭제 중 오류가 발생한 경우
    """
    try:
        return await delete_and_commit(db, db_comment)
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"댓글 삭제 중 오류가 발생했습니다: {err.orig}",
        ) from err
