from typing import cast

from fastapi import HTTPException
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


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> models.User | None:
    """
    사용자의 이메일과 비밀번호로 인증을 시도합니다.

    :param db: 비동기 데이터베이스 세션
    :param email: 사용자 이메일
    :param password: 사용자 비밀번호
    :return: 인증된 사용자 모델 또는 None
    """
    db_user = await crud.get_user_by_email(db=db, email=email)
    if not db_user:
        return None

    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="사용자가 비활성화되었습니다.",
        )

    if not verify_password(password, cast(str, db_user.hashed_password)):
        return None

    return db_user


async def get_user_profile(db: AsyncSession, db_user: models.User) -> models.User:
    """
    사용자 ID로 사용자의 프로필을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 조회할 사용자 ID
    :return: 사용자 모델
    """
    return await crud.get_user(db=db, user_id=cast(str, db_user.id))


async def update_user_profile(
    db: AsyncSession, db_user: models.User, user_update: schemas.UserUpdate
) -> models.User:
    """
    사용자 프로필을 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :param user_update: 사용자 업데이트 스키마
    :return: 업데이트된 사용자 모델
    """
    updated_user = await crud.update_user(
        db=db, db_user=db_user, user_update=user_update
    )
    return updated_user


async def deactivate_user(db: AsyncSession, db_user: models.User) -> models.User:
    """
    사용자를 비활성화합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :return: 비활성화된 사용자 모델
    """
    deactivated_user = await crud.deactivate_user(db=db, db_user=db_user)
    return deactivated_user


async def delete_user(db: AsyncSession, db_user: models.User) -> None:
    """
    사용자를 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :return: None
    """
    await crud.delete_user(db=db, user_id=cast(str, db_user.id))


async def update_admin_status(
    db: AsyncSession, db_user: models.User, is_admin: bool
) -> models.User:
    """
    사용자의 관리자 상태를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :return: 업데이트된 사용자 모델
    """
    updated_user = await crud.update_admin_status(
        db=db, db_user=db_user, is_admin=is_admin
    )
    return updated_user


async def update_password(
    db: AsyncSession, db_user: models.User, new_password: str
) -> models.User:
    """
    사용자의 비밀번호를 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 데이터베이스에서 조회된 사용자 모델
    :param new_password: 새 비밀번호
    :return: 업데이트된 사용자 모델
    """
    hashed_password = hash_password(new_password)
    updated_user = await crud.update_password(
        db=db, db_user=db_user, hashed_password=hashed_password
    )
    return updated_user
