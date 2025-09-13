from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.crud import add_and_commit, commit_and_refresh, delete_and_commit
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdateProfile


async def create_user(
    db: AsyncSession, user_in: UserCreate, hashed_password: str
) -> User:
    """
    새로운 사용자를 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_in: 사용자 생성 스키마
    :param hashed_password: 해시된 비밀번호 (서비스 계층에서 제공)
    :return: 생성된 사용자 모델
    :raises HTTPException: 이메일 또는 사용자 이름이 이미 존재하는 경우
    """
    create_data = user_in.model_dump(mode="json", exclude={"password"})
    db_user = User(
        **create_data,
        hashed_password=hashed_password,
    )

    try:
        return await add_and_commit(db, db_user)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일 또는 사용자 이름입니다.",
        ) from err


async def get_user(db: AsyncSession, user_id: str) -> User | None:
    """
    활성화된 사용자를 ID로 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 조회할 사용자 ID
    :return: 사용자 모델 또는 None
    """
    stmt = User.active_query().where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    활성화된 사용자를 이메일로 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param email: 조회할 사용자 이메일
    :return: 사용자 모델 또는 None
    """
    stmt = User.active_query().where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    활성화된 사용자를 사용자 이름으로 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param username: 조회할 사용자 이름
    :return: 사용자 모델 또는 None
    """
    stmt = User.active_query().where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[User]:
    """
    활성화된 사용자 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param skip: 건너뛸 사용자 수
    :param limit: 조회할 최대 사용자 수
    :return: 사용자 모델 리스트
    """
    stmt = (
        User.active_query().order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_user(
    db: AsyncSession, db_user: User, user_update: UserUpdateProfile
) -> User:
    """
    사용자의 정보를 업데이트합니다. (사용자 이름, 프로필 이미지)

    :param db: 비동기 데이터베이스 세션
    :param db_user: 업데이트할 사용자 모델
    :param user_update: 사용자 업데이트 스키마
    :return: 업데이트된 사용자 모델
    :raises HTTPException: 사용자 이름이 이미 존재하는 경우
    """
    update_data = user_update.model_dump(mode="json", exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        return await commit_and_refresh(db, db_user)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="사용자 정보가 이미 존재합니다.",
        ) from err


async def deactivate_user(db: AsyncSession, db_user: User) -> User:
    """
    사용자를 비활성화하고 논리적으로 삭제합니다 (Soft Delete).
    is_active를 False로, deleted_at에 현재 시간을 설정합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 비활성화할 사용자 모델
    :return: 비활성화된 사용자 모델
    :raises HTTPException: 비활성화 중 오류가 발생한 경우
    """
    if db_user.is_active and db_user.deleted_at is None:
        db_user.is_active = False
        db_user.deleted_at = datetime.now(timezone.utc)
        try:
            return await commit_and_refresh(db, db_user)
        except SQLAlchemyError as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 비활성화 중 데이터베이스 오류가 발생했습니다.",
            ) from err
    return db_user


async def delete_user(db: AsyncSession, db_user: User) -> bool:
    """
    사용자를 데이터베이스에서 물리적으로 삭제합니다 (Hard Delete).

    :param db: 비동기 데이터베이스 세션
    :param db_user: 삭제할 사용자 모델
    :return: 성공 시 True
    :raises HTTPException: 삭제 중 무결성 오류가 발생한 경우
    """
    try:
        return await delete_and_commit(db, db_user)
    except IntegrityError as err:
        # 자식 레코드가 존재하여 삭제할 수 없는 경우
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="사용자를 삭제할 수 없습니다. 관련된 데이터(게시글 등)가 존재합니다.",
        ) from err


async def update_admin_status(db: AsyncSession, db_user: User, is_admin: bool) -> User:
    """
    사용자의 관리자 상태를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 업데이트할 사용자 모델
    :param is_admin: 새로운 관리자 상태
    :return: 업데이트된 사용자 모델
    :raises HTTPException: 관리자 상태 업데이트 중 오류가 발생한 경우
    """
    if db_user.is_admin != is_admin:
        db_user.is_admin = is_admin
        try:
            return await commit_and_refresh(db, db_user)
        except SQLAlchemyError as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 관리자 상태 업데이트 중 데이터베이스 오류가 발생했습니다.",
            ) from err
    return db_user


async def update_password(
    db: AsyncSession, db_user: User, hashed_password: str
) -> User:
    """
    사용자의 비밀번호를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 업데이트할 사용자 모델
    :param hashed_password: 새로운 해시된 비밀번호
    :return: 업데이트된 사용자 모델
    :raises HTTPException: 비밀번호 업데이트 중 오류가 발생한 경우
    """
    db_user.hashed_password = hashed_password
    try:
        return await commit_and_refresh(db, db_user)
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 비밀번호 업데이트 중 데이터베이스 오류가 발생했습니다.",
        ) from err
