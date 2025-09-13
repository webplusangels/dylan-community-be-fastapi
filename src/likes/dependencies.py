from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from src.auth.dependencies import get_current_active_user
from src.db.session import DbSession
from src.likes import crud
from src.likes.models import PostLike
from src.users.models import User


async def get_like_by_post_and_user_or_404(
    db: DbSession,
    post_id: str = Path(..., description="게시글 ID"),
    user_id: str = Path(..., description="사용자 ID"),
) -> PostLike:
    """
    경로 매개변수에서 post_id와 user_id를 받아 해당 좋아요를 조회하고,
    없으면 404 오류를 발생시키는 의존성 함수.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param user_id: 사용자 ID
    :return: 좋아요 모델
    :raises HTTPException: 좋아요가 존재하지 않는 경우 404 오류
    """
    like = await crud.get_like(db=db, post_id=post_id, user_id=user_id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"좋아요를 찾을 수 없습니다. {post_id=}, {user_id=}",
        )
    return like


async def require_like_owner(
    db_like: Annotated[PostLike, Depends(get_like_by_post_and_user_or_404)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PostLike:
    """
    좋아요 소유자 권한이 있는지 확인하는 의존성 함수.
    본인이 누른 좋아요가 아니면 권한 오류를 발생시킵니다.

    :param db_like: 의존성으로 조회된 좋아요 모델
    :param current_user: 현재 로그인한 사용자 모델
    :return: 좋아요 모델 (소유자 권한 확인 후 반환)
    :raises HTTPException: 권한이 없는 경우 403 오류 발생
    """
    if db_like.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="좋아요를 삭제할 권한이 없습니다.",
        )
    return db_like


async def get_like_by_post_and_current_user(
    db: DbSession,
    post_id: str = Path(..., description="게시글 ID"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
) -> PostLike | None:
    """
    현재 사용자가 특정 게시글에 누른 좋아요를 조회합니다.
    좋아요가 없어도 오류를 발생시키지 않습니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param current_user: 현재 로그인한 사용자 모델
    :return: 좋아요 모델 또는 None
    """
    if not current_user:
        return None

    return await crud.get_like(db=db, post_id=post_id, user_id=current_user.id)


# 타입 별칭
ValidLike = Annotated[PostLike, Depends(get_like_by_post_and_user_or_404)]
OwnerLike = Annotated[PostLike, Depends(require_like_owner)]
OptionalUserLike = Annotated[
    PostLike | None, Depends(get_like_by_post_and_current_user)
]
