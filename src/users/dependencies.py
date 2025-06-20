from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.db.session import get_async_db
from src.users import crud, models


async def get_user_by_id_or_404(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user_id: str = Path(),
) -> models.User:
    """
    경로 매개변수에서 user_id를 받아 사용자를 조회하고,
    없으면 404 예외를 발생시키는 의존성 함수.
    """
    user = await crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다."
        )
    return user


def require_admin(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
) -> models.User:
    """
    현재 사용자가 권한을 가지고 있는지 확인하는 의존성 함수. (관리자 권한 필요)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user


def require_self_or_admin(
    db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
    current_user: Annotated[models.User, Depends(get_current_active_user)],
) -> models.User:
    """
    현재 사용자가 자신의 프로필을 수정할 수 있는지 확인하는 의존성 함수.
    본인 프로필이 아니면 관리자 권한이 필요합니다.
    """
    if db_user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다.",
        )
    return db_user


# 타입 별칭 정의
SelfUser = Annotated[models.User, Depends(get_current_active_user)]
AdminUser = Annotated[models.User, Depends(require_admin)]
SelfOrAdminUsers = Annotated[models.User, Depends(require_self_or_admin)]
