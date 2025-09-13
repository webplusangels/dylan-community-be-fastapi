from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.crud import add_and_commit, delete_and_commit
from src.likes.models import PostLike
from src.likes.schemas import PostLikeBase


async def create_like(db: AsyncSession, like_in: PostLikeBase) -> PostLike:
    """
    새로운 좋아요를 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param like_in: 좋아요 생성 스키마
    :return: 생성된 좋아요 모델
    :raises HTTPException: 좋아요 생성 중 오류가 발생한 경우
    """
    db_like = PostLike(**like_in.model_dump())
    try:
        await add_and_commit(db, db_like)
        return db_like
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"좋아요 생성 중 오류가 발생했습니다: {err.orig}",
        ) from err


async def get_like(db: AsyncSession, post_id: str, user_id: str) -> PostLike | None:
    """
    특정 게시글에 대한 사용자의 좋아요를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param user_id: 사용자 ID
    :return: 좋아요 모델 또는 None
    """
    stmt = select(PostLike).where(
        PostLike.post_id == post_id, PostLike.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_likes_by_post(
    db: AsyncSession, post_id: str, skip: int = 0, limit: int = 10
) -> Sequence[PostLike]:
    """
    특정 게시글의 좋아요 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 좋아요 수 (페이징)
    :return: 좋아요 모델 리스트
    """
    stmt = (
        select(PostLike)
        .where(PostLike.post_id == post_id)
        .order_by(PostLike.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_likes_by_user(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10
) -> Sequence[PostLike]:
    """
    특정 사용자의 좋아요 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 사용자 ID
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 좋아요 수 (페이징)
    :return: 좋아요 모델 리스트
    """
    stmt = (
        select(PostLike)
        .where(PostLike.user_id == user_id)
        .order_by(PostLike.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_total_likes_count_by_post(db: AsyncSession, post_id: str) -> int:
    """
    특정 게시글의 총 좋아요 수를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :return: 총 좋아요 수
    """
    stmt = select(func.count(PostLike.post_id)).where(PostLike.post_id == post_id)
    result = await db.execute(stmt)
    return result.scalar() or 0


async def get_total_likes_count_by_user(db: AsyncSession, user_id: str) -> int:
    """
    특정 사용자의 총 좋아요 수를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 사용자 ID
    :return: 총 좋아요 수
    """
    stmt = select(func.count(PostLike.user_id)).where(PostLike.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar() or 0


async def delete_like(db: AsyncSession, db_like: PostLike) -> bool:
    """
    좋아요를 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_like: 삭제할 좋아요 모델
    :return: 삭제 성공 여부
    :raises HTTPException: 좋아요 삭제 중 오류가 발생한 경우
    """
    try:
        return await delete_and_commit(db, db_like)
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"좋아요 삭제 중 오류가 발생했습니다: {err.orig}",
        ) from err
