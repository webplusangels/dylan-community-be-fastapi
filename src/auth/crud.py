from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import TokenBlocklist
from src.users import crud as user_crud


async def add_token_to_blocklist(
    db: AsyncSession, jti: str, expires_at: datetime, user_id: str
) -> None:
    """
    jti를 블락리스트에 추가합니다.

    :param db: 비동기 데이터베이스 세션
    :param jti: 토큰의 고유 식별자 (jti)
    :param expires_at: 토큰의 만료 시간
    :param user_id: 사용자의 고유 식별자
    """
    blocklist_entry = TokenBlocklist(jti=jti, expires_at=expires_at, user_id=user_id)
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


async def invalidate_user_tokens(db: AsyncSession, user_id: str) -> None:
    """
    사용자의 모든 토큰을 블락리스트에 추가합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 사용자의 고유 식별자
    """
    user = await user_crud.get_user(db=db, user_id=user_id)
    if user is None:
        return

    user.token_version += 1
    await db.commit()


async def cleanup_expired_tokens(
    db: AsyncSession,
) -> None:
    """
    블락리스트에서 만료된 토큰을 제거합니다.

    :param db: 비동기 데이터베이스 세션
    """
    await db.execute(
        delete(TokenBlocklist).where(
            TokenBlocklist.expires_at < datetime.now(timezone.utc)
        )
    )
    await db.commit()
