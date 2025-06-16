from typing import Annotated

from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

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
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user
