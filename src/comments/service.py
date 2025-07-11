from typing import Sequence, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.comments import crud, models, schemas
from src.users.models import User as models_User


async def create_comment(
    db: AsyncSession, comment_create: schemas.CommentCreate, db_user: models_User
) -> models.PostComment:
    """
    새로운 댓글을 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param comment_create: 댓글 생성 스키마
    :param db_user: 댓글 작성자의 사용자 모델
    :return: 생성된 댓글 모델
    """
    created_comment = await crud.create_comment(
        db=db, comment_in=comment_create, user_id=db_user.id
    )

    return created_comment


async def get_comment_by_id(db: AsyncSession, comment_id: str) -> models.PostComment:
    """
    댓글 ID로 댓글을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 데이터베이스에서 조회된 댓글 모델
    :return: 조회된 댓글 모델
    """
    comment = await crud.get_comment(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다.",
        )
    return comment


async def get_comments_with_total_count_by_post(
    db: AsyncSession, post_id: str, skip: int = 0, limit: int = 10
) -> Tuple[Sequence[models.PostComment], int]:
    """
    게시글에 대한 댓글 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 댓글이 속한 게시글 ID
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 댓글 수 (페이징)
    :return: 댓글 모델 리스트와 총 댓글 수
    """
    comments = await crud.get_comments(db=db, post_id=post_id, skip=skip, limit=limit)
    total_count = await crud.get_total_comments_count(db=db, post_id=post_id)
    return comments, total_count


async def update_comment(
    db: AsyncSession,
    db_comment: models.PostComment,
    comment_update: schemas.CommentUpdate,
) -> models.PostComment:
    """
    댓글을 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 데이터베이스에서 조회된 댓글 모델
    :param comment_update: 댓글 업데이트 스키마
    :return: 업데이트된 댓글 모델
    """
    updated_comment = await crud.update_comment(
        db=db, db_comment=db_comment, comment_update=comment_update
    )
    return updated_comment


async def deactivate_comment(
    db: AsyncSession,
    db_comment: models.PostComment,
) -> models.PostComment:
    """
    댓글을 비활성화(soft delete)합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 데이터베이스에서 조회된 댓글 모델
    :return: 비활성화된 댓글 모델
    """
    deactivated_comment = await crud.deactivate_comment(db=db, db_comment=db_comment)
    return deactivated_comment


async def delete_comment(
    db: AsyncSession,
    db_comment: models.PostComment,
) -> None:
    """
    댓글을 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 데이터베이스에서 조회된 댓글 모델
    :return: None
    """
    await crud.delete_comment(db=db, db_comment=db_comment)
    return
