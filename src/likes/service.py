from typing import Sequence, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes import crud
from src.likes.models import PostLike
from src.likes.schemas import PostLikeBase
from src.users.models import User


async def create_like(db: AsyncSession, post_id: str, db_user: User) -> PostLike:
    """
    새로운 좋아요를 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param db_user: 좋아요를 누른 사용자 모델
    :return: 생성된 좋아요 모델
    :raises HTTPException: 이미 좋아요가 존재하는 경우
    """
    # 중복 좋아요 확인
    existing_like = await crud.get_like(db=db, post_id=post_id, user_id=db_user.id)
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 좋아요를 누른 게시글입니다.",
        )

    like_in = PostLikeBase(post_id=post_id, user_id=db_user.id)
    created_like = await crud.create_like(db=db, like_in=like_in)
    return created_like


async def get_like_by_post_and_user(
    db: AsyncSession, post_id: str, user_id: str
) -> PostLike | None:
    """
    특정 게시글에 대한 사용자의 좋아요를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param user_id: 사용자 ID
    :return: 좋아요 모델 또는 None
    """
    return await crud.get_like(db=db, post_id=post_id, user_id=user_id)


async def get_likes_with_total_count_by_post(
    db: AsyncSession, post_id: str, skip: int = 0, limit: int = 10
) -> Tuple[Sequence[PostLike], int]:
    """
    특정 게시글의 좋아요 목록과 총 좋아요 수를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID (유효성은 라우터에서 확인됨)
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 좋아요 수 (페이징)
    :return: (좋아요 모델 리스트, 총 좋아요 수) 튜플
    """
    likes = await crud.get_likes_by_post(db=db, post_id=post_id, skip=skip, limit=limit)
    total_count = await crud.get_total_likes_count_by_post(db=db, post_id=post_id)
    return likes, total_count


async def get_likes_with_total_count_by_user(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10
) -> Tuple[Sequence[PostLike], int]:
    """
    특정 사용자의 좋아요 목록과 총 좋아요 수를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 사용자 ID (유효성은 라우터에서 확인됨)
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 좋아요 수 (페이징)
    :return: (좋아요 모델 리스트, 총 좋아요 수) 튜플
    """
    likes = await crud.get_likes_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    total_count = await crud.get_total_likes_count_by_user(db=db, user_id=user_id)
    return likes, total_count


async def delete_like(db: AsyncSession, db_like: PostLike) -> bool:
    """
    좋아요를 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_like: 삭제할 좋아요 모델
    :return: 삭제 성공 여부
    """
    return await crud.delete_like(db=db, db_like=db_like)


async def toggle_like(
    db: AsyncSession, post_id: str, db_user: User
) -> Tuple[PostLike | None, bool]:
    """
    좋아요를 토글합니다 (있으면 삭제, 없으면 생성).

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param db_user: 사용자 모델
    :return: (좋아요 모델 또는 None, 생성 여부) 튜플
    """
    existing_like = await crud.get_like(db=db, post_id=post_id, user_id=db_user.id)

    if existing_like:
        # 기존 좋아요가 있으면 삭제
        await crud.delete_like(db=db, db_like=existing_like)
        return None, False
    else:
        # 기존 좋아요가 없으면 생성
        like_in = PostLikeBase(post_id=post_id, user_id=db_user.id)
        created_like = await crud.create_like(db=db, like_in=like_in)
        return created_like, True
