from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import TokenBlocklist


async def add_token_to_blocklist(
    db: AsyncSession, jti: str, expires_at: datetime
) -> None:
    """
    jti를 블락리스트에 추가합니다.

    :param db: 비동기 데이터베이스 세션
    :param jti: 토큰의 고유 식별자 (jti)
    :param expires_at: 토큰의 만료 시간
    """
    blocklist_entry = TokenBlocklist(jti=jti, expires_at=expires_at)
    db.add(blocklist_entry)
    await db.commit()


async def is_token_blocked(db: AsyncSession, jti: str) -> bool:
    """
    jti가 블락리스트에 있는지 확인합니다.

    :param db: 비동기 데이터베이스 세션
    :param jti: 토큰의 고유 식별자 (jti)
    :return: 블락리스트에 있으면 True, 아니면 False
    """
    result = await db.execute(select(TokenBlocklist).where(TokenBlocklist.jti == jti))
    return result.scalars().first() is not None
