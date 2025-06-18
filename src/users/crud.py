from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate


async def _commit_and_refresh(db: AsyncSession, instance: User) -> User:
    """
    데이터베이스에 변경 사항을 커밋하고 인스턴스를 새로 고칩니다.

    :param db: 비동기 데이터베이스 세션
    :param instance: 새로 고칠 인스턴스
    :return: 새로 고친 인스턴스
    :raises: DB 관련 예외를 그대로 전파
    """
    try:
        await db.commit()
        await db.refresh(instance)
        return instance
    except Exception:
        await db.rollback()
        raise  # 호출자가 구체적인 예외 처리


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
    create_data = user_in.model_dump(mode="json")
    create_data.pop(
        "password", None
    )  #  User 모델에 없는 'password' 필드를 딕셔너리에서 제거
    db_user = User(
        **create_data,
        hashed_password=hashed_password,
    )

    db.add(db_user)
    try:
        return await _commit_and_refresh(db, db_user)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일 또는 사용자 이름입니다.",
        ) from err


async def get_user(db: AsyncSession, user_id: str) -> User | None:
    """
    사용자 ID로 사용자를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 조회할 사용자 ID
    :return: 사용자 모델 또는 None
    """
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    이메일로 사용자를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param email: 조회할 사용자 이메일
    :return: 사용자 모델 또는 None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    사용자 이름으로 사용자를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param username: 조회할 사용자 이름
    :return: 사용자 모델 또는 None
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


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
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )

    return result.scalars().all()


async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate) -> User:
    """
    사용자의 정보를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 업데이트할 사용자 모델
    :param user_update: 사용자 업데이트 스키마
    :return: 업데이트된 사용자 모델
    :raises HTTPException: 사용자 이름이 이미 존재하는 경우
    """
    update_data = user_update.model_dump(mode="json", exclude_unset=True)
    is_updated = False

    for key, value in update_data.items():
        if getattr(db_user, key) != value:
            setattr(db_user, key, value)
            is_updated = True

    # 변경된 내용이 있는 경우에만 커밋
    if is_updated:
        try:
            return await _commit_and_refresh(db, db_user)
        except IntegrityError as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="사용자 정보가 이미 존재합니다.",
            ) from err

    return db_user


async def deactivate_user(db: AsyncSession, db_user: User) -> User:
    """
    사용자를 비활성화합니다 (논리적 삭제).

    :param db: 비동기 데이터베이스 세션
    :param db_user: 비활성화할 사용자 모델
    :return: 비활성화된 사용자 모델
    :raises HTTPException: 비활성화 중 오류가 발생한 경우
    """
    if db_user.is_active:
        db_user.is_active = False
        try:
            return await _commit_and_refresh(db, db_user)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 비활성화 중 오류가 발생했습니다.",
            ) from err
    return db_user


async def delete_user(db: AsyncSession, db_user: User) -> bool:
    """
    사용자를 데이터베이스에서 물리적으로 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 삭제할 사용자 모델
    :return: 성공 시 True, 대상이 없을 시 False
    :raises HTTPException: 삭제 중 무결성 오류가 발생한 경우
    """
    try:
        await db.delete(db_user)
        await db.commit()
        return True
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="사용자를 삭제할 수 없습니다. 관련된 데이터가 존재합니다.",
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
            return await _commit_and_refresh(db, db_user)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 관리자 상태 업데이트 중 서버 오류가 발생했습니다.",
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
        return await _commit_and_refresh(db, db_user)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 비밀번호 업데이트 중 서버 오류가 발생했습니다.",
        ) from err
