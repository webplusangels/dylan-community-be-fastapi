from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import AsyncSessionLocal


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션 의존성입니다.

    FastAPI는 async generator (yield 사용) 형태의 dependency를 지원하므로
    여기서 직접 AsyncSession 인스턴스를 yield 합니다. 이전에
    `@asynccontextmanager`로 감싸인 함수는 호출 시 async context manager
    객체를 반환해 FastAPI가 세션 인스턴스 대신 컨텍스트 매니저를 전달하게
    되어 `AttributeError`가 발생했습니다.
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


# 별칭 정의: 라우트에서 `db: DbSession`으로 주입하면 AsyncSession 인스턴스를 받습니다
DbSession = Annotated[AsyncSession, Depends(get_async_db)]
