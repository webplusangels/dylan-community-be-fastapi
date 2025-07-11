from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from src.auth.dependencies import get_current_active_user
from src.db.session import DbSession
from src.posts import crud, models
from src.users.models import User as models_User


async def get_post_by_id_or_404(
    db: DbSession,
    post_id: str = Path(),
) -> models.Post:
    """
    경로 매개변수에서 post_id를 받아 게시글을 조회하고,
    없으면 404 예외를 발생시키는 의존성 함수.
    """
    post = await crud.get_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"게시글을 찾을 수 없습니다. {post_id=}",
        )
    return post


def require_author_or_admin(
    db_post: Annotated[models.Post, Depends(get_post_by_id_or_404)],
    current_user: Annotated[models_User, Depends(get_current_active_user)],
) -> models.Post:
    """
    현재 사용자가 게시글 작성자이거나 관리자 권한이 있는지 확인하는 의존성 함수.
    본인 게시글이 아니면 관리자 권한이 필요합니다.
    """
    if db_post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글 작성자만 수정할 수 있습니다.",
        )
    return db_post


# 타입 별칭 정의
ValidPost = Annotated[models.Post, Depends(get_post_by_id_or_404)]
AuthorOrAdminPost = Annotated[models.Post, Depends(require_author_or_admin)]
