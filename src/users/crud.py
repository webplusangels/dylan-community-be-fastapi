from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    이메일로 사용자를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param email: 조회할 사용자 이메일
    :return: 사용자 모델 또는 None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(
    db: AsyncSession, user_in: UserCreate, hashed_password: str
) -> User:
    """
    새로운 사용자를 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_in: 사용자 생성 스키마
    :param hashed_password: 해시된 비밀번호 (서비스 계층에서 제공)
    :return: 생성된 사용자 모델
    """
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        profile_image_path=user_in.profile_image_path,
    )
    db.add(db_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: str) -> User | None:
    """
    사용자 ID로 사용자를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 조회할 사용자 ID
    :return: 사용자 모델 또는 None
    """
    return await db.get(User, user_id)


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[User]:
    """
    사용자 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param skip: 건너뛸 사용자 수
    :param limit: 조회할 최대 사용자 수
    :return: 사용자 모델 리스트
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate) -> User:
    """
    사용자의 정보를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 업데이트할 사용자 모델
    :param user_update: 사용자 업데이트 스키마
    :return: 업데이트된 사용자 모델
    """
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    # 변경된 내용이 있는 경우에만 커밋
    if db.is_modified(db_user):
        await db.commit()
        await db.refresh(db_user)

    return db_user
