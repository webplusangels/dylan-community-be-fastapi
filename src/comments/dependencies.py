from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select

from src.auth.dependencies import get_current_active_user
from src.comments import crud, models
from src.db.session import DbSession
from src.users.models import User as models_User


async def get_comments_by_id_or_404(
    db: DbSession, comment_id: str = Path()
) -> models.PostComment:
    """
    경로 매개변수에서 comment_id를 받아 해당 댓글을 조회하고,
    없으면 404 오류를 발생시키는 의존성 함수.
    """
    comment = await crud.get_comment(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"댓글을 찾을 수 없습니다. {comment_id=}",
        )
    # Ensure the author relationship is loaded while we're still in async
    # context. If Pydantic tries to access `author` later and it is not
    # loaded, SQLAlchemy would attempt IO from sync code and raise
    # MissingGreenlet. Load the User explicitly and attach it to the
    # comment instance.
    if comment.user_id is not None:
        stmt = select(models_User).where(models_User.id == comment.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        # attach user to the relationship attribute so later access won't
        # trigger lazy async IO
        comment.author = user
        # touch some simple attributes while still in async context so
        # they're available synchronously during response serialization.
        if user is not None:
            _ = user.id
            _ = user.username
    return comment


async def require_comment_author_or_admin(
    db_comment: Annotated[models.PostComment, Depends(get_comments_by_id_or_404)],
    current_user: Annotated[models_User, Depends(get_current_active_user)],
) -> models.PostComment:
    """
    댓글 작성자이거나 관리자 권한이 있는지 확인하는 의존성 함수.
    """
    if db_comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 작성자만 수정할 수 있습니다.",
        )
    return db_comment


ValidComment = Annotated[models.PostComment, Depends(get_comments_by_id_or_404)]
AuthorOrAdminComment = Annotated[
    models.PostComment, Depends(require_comment_author_or_admin)
]
