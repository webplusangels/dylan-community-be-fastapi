from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password, verify_password
from src.users import crud, models, schemas


async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    """
    새로운 사용자를 생성하는 비즈니스 로직입니다.

    :param db: 비동기 데이터베이스 세션
    :param user_in: 사용자 생성 스키마
    :return: 생성된 사용자 모델
    """
    # 서비스 계층에서는 어떻게 만들지에만 집중하고,
    # CRUD 계층에서 중복 확인을 처리합니다.

    # 비밀번호 해싱
    hashed_password = hash_password(user_in.password)

    # 사용자 생성
    created_user = await crud.create_user(
        db=db, user_in=user_in, hashed_password=hashed_password
    )

    return created_user


async def get_user_profile(db_user: models.User) -> models.User:
    """
    사용자 프로필을 조회합니다.

    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :return: 사용자 모델
    """
    return db_user


async def get_all_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[models.User]:
    """
    모든 사용자를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param skip: 건너뛸 사용자 수
    :param limit: 조회할 최대 사용자 수
    :return: 사용자 모델 리스트
    """
    users = await crud.get_users(db=db, skip=skip, limit=limit)
    return users


async def update_user_profile(
    db: AsyncSession,
    db_user: models.User,
    user_update: schemas.UserUpdate,
) -> models.User:
    """
    사용자 프로필을 업데이트합니다. 본인 혹은 관리자가 다른 사용자의 프로필을 업데이트할 수 있습니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :param user_update: 사용자 업데이트 스키마
    :return: 업데이트된 사용자 모델
    """
    updated_user = await crud.update_user(
        db=db, db_user=db_user, user_update=user_update
    )
    return updated_user


async def deactivate_user(
    db: AsyncSession,
    db_user: models.User,
) -> models.User:
    """
    사용자를 비활성화합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :return: 비활성화된 사용자 모델
    """
    deactivated_user = await crud.deactivate_user(db=db, db_user=db_user)
    return deactivated_user


async def delete_user(
    db: AsyncSession,
    db_user: models.User,
) -> None:
    """
    사용자를 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델'
    :return: None
    """
    await crud.delete_user(db=db, db_user=db_user)


async def update_admin_status(
    db: AsyncSession, db_user: models.User, is_admin: bool, current_user: models.User
) -> models.User:
    """
    사용자의 관리자 상태를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :param is_admin: 새 관리자 상태 (True/False)
    :param current_user: 현재 로그인한 사용자 모델 (권한 확인용)
    :return: 업데이트된 사용자 모델
    """
    # 관리자가 자신의 권한을 해제하려는 경우 예외 처리
    if db_user.id == current_user.id and current_user.is_admin and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="관리자는 자신의 관리자 권한을 해제할 수 없습니다.",
        )
    updated_user = await crud.update_admin_status(
        db=db, db_user=db_user, is_admin=is_admin
    )
    return updated_user


async def update_password(
    db: AsyncSession,
    db_user: models.User,
    password_update: schemas.UserUpdatePassword,
) -> models.User:
    """
    사용자의 비밀번호를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :param password_update: 새 비밀번호 스키마
    :return: 업데이트된 사용자 모델
    """
    if not verify_password(
        password_update.current_password, str(db_user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다.",
        )

    if verify_password(password_update.new_password, str(db_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호가 현재 비밀번호와 동일합니다.",
        )

    hashed_password = hash_password(password_update.new_password)
    updated_user = await crud.update_password(
        db=db, db_user=db_user, hashed_password=hashed_password
    )
    return updated_user
