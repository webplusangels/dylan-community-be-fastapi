from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import AsyncSessionLocal


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션을 생성하고 변환하는 제너레이터 함수입니다.
    사용 후 세션을 닫습니다.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# 별칭 정의
DbSession = AsyncGenerator[AsyncSession, Depends(get_async_db)]
