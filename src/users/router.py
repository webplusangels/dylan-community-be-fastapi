from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_db
from src.users import models, schemas, service
from src.users.dependencies import (
    AdminUser,
    SelfOrAdminUsers,
    SelfUser,
    get_user_by_id_or_404,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다. 성공 시 사용자 정보를 반환합니다.",
)
async def create_user(
    user_in: schemas.UserCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> models.User:
    """
    새로운 사용자를 생성합니다. 성공 시 사용자 정보를 반환합니다.

    :param user_in: 사용자 생성 스키마
    :param db: 비동기 데이터베이스 세션
    :return: 생성된 사용자 모델
    """
    created_user = await service.create_user(db=db, user_in=user_in)
    return created_user


@router.get(
    "/",
    response_model=Sequence[schemas.UserRead],
    status_code=status.HTTP_200_OK,
    summary="모든 사용자 조회",
    description="모든 사용자를 조회합니다. 성공 시 사용자 목록을 반환합니다.",
)
async def handle_get_all_users(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    _current_user: AdminUser,
    skip: int = Query(0, ge=0, description="건너뛸 사용자 수"),
    limit: int = Query(100, ge=1, le=100, description="조회할 최대 사용자 수"),
) -> Sequence[models.User]:
    """
    모든 사용자를 조회합니다. 성공 시 사용자 목록을 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param _current_user: 현재 로그인한 사용자 모델 (관리자 권한 확인용)
    :param skip: 건너뛸 사용자 수 (기본값: 0)
    :param limit: 조회할 최대 사용자 수 (기본값: 100, 최소 1, 최대 100)
    :return: 사용자 모델 리스트
    """
    users = await service.get_all_users(db=db, skip=skip, limit=limit)
    return users


@router.get(
    "/me",
    response_model=schemas.UserProfilePublic,
    status_code=status.HTTP_200_OK,
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다. 성공 시 사용자 프로필 정보를 반환합니다.",
)
async def get_my_profile(
    current_user: SelfUser,
) -> models.User:
    """
    현재 로그인한 사용자의 프로필 정보를 조회
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
    summary="사용자 조회",
    description="사용자 ID로 사용자를 조회합니다. 성공 시 사용자 정보를 반환합니다.",
)
async def handle_get_user(db_user: SelfOrAdminUsers) -> models.User:
    """
    사용자 ID로 사용자를 조회합니다. 성공 시 사용자 정보를 반환합니다.

    :param db_user: 사용자 ID로 조회할 사용자 모델 (의존성 주입을 통해 조회)
    :return: 조회된 사용자 모델
    """
    return db_user


@router.patch(
    "/{user_id}",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
    summary="사용자 정보 수정",
    description="사용자 ID로 사용자의 정보를 수정합니다. 성공 시 수정된 사용자 정보를 반환합니다.",
)
async def handle_update_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    db_user: SelfOrAdminUsers,
    user_update: schemas.UserUpdate,
) -> models.User:
    """
    사용자 ID로 사용자의 정보를 수정합니다. 성공 시 수정된 사용자 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 사용자 ID로 조회할 사용자 모델 (의존성 주입을 통해 조회)
    :param user_update: 사용자 업데이트 스키마
    :return: 수정된 사용자 모델
    """
    # db에 commit을 해야 하므로 db를 인자로 받음
    updated_user = await service.update_user_profile(
        db=db, db_user=db_user, user_update=user_update
    )
    return updated_user


@router.patch(
    "/{user_id}/password",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
    summary="비밀번호 변경",
    description="사용자 ID로 사용자의 비밀번호를 변경합니다. 성공 시 업데이트된 사용자 정보를 반환합니다.",
)
async def handle_change_password(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    db_user: SelfOrAdminUsers,
    password_update: schemas.UserUpdatePassword,
) -> models.User:
    """
    사용자 ID로 사용자의 비밀번호를 변경합니다. 성공 시 업데이트된 사용자 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 사용자 ID로 조회할 사용자 모델 (의존성 주입을 통해 조회)
    :param password_update: 비밀번호 업데이트 스키마
    :return: 업데이트된 사용자 모델
    """
    updated_user = await service.update_password(
        db=db, db_user=db_user, password_update=password_update
    )
    return updated_user


@router.patch(
    "/{user_id}/deactivate",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
    summary="사용자 비활성화",
    description="사용자 ID로 사용자를 비활성화합니다. 성공 시 비활성화된 사용자 정보를 반환합니다.",
)
async def handle_deactivate_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    db_user: SelfOrAdminUsers,
) -> models.User:
    """
    사용자 ID로 사용자를 비활성화합니다. 성공 시 비활성화된 사용자 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 사용자 ID로 조회할 사용자 모델 (의존성 주입을 통해 조회)
    :return: 비활성화된 사용자 모델
    """
    deactivated_user = await service.deactivate_user(db=db, db_user=db_user)
    return deactivated_user


@router.patch(
    "/{user_id}/admin",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
    summary="관리자 권한 업데이트",
    description="사용자 ID로 사용자의 관리자 권한을 업데이트합니다. 성공 시 업데이트된 사용자 정보를 반환합니다.",
)
async def handle_update_admin_status(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
    admin_update: schemas.UserUpdateAdmin,
    current_user: AdminUser,
) -> models.User:
    """
    사용자 ID로 사용자의 관리자 권한을 업데이트합니다. 성공 시 업데이트된 사용자 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 관리자 권한을 업데이트할 사용자 모델 (의존성 주입을 통해 조회)
    :param admin_update: 관리자 권한 업데이트 스키마
    :param _current_user: 현재 로그인한 사용자 모델 (권한 확인용)
    :return: 업데이트된 사용자 모델
    """
    updated_user = await service.update_admin_status(
        db=db,
        db_user=db_user,
        is_admin=admin_update.is_admin,
        current_user=current_user,
    )
    return updated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    description="사용자 ID로 사용자를 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.",
)
async def handle_delete_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
    _current_user: AdminUser,
) -> None:
    """
    사용자 ID로 사용자를 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.

    :param db_user: 삭제할 사용자 모델 (의존성 주입을 통해 조회)
    :param db: 비동기 데이터베이스 세션
    :param _current_user: 현재 로그인한 사용자 모델 (권한 확인용)
    :return: None
    """
    await service.delete_user(db=db, db_user=db_user)
