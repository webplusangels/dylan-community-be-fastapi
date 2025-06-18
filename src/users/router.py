from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.db.session import get_async_db
from src.users import models, schemas, service

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
    :raises Exception: 예상치 못한 예외 발생 시 500 에러
    """
    try:
        created_user = await service.create_user(db=db, user_in=user_in)
        return created_user
    except HTTPException:
        # 이미 HTTPException이면 그대로 전달
        raise
    except Exception as e:
        # 예상치 못한 예외 발생 시 500 에러
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        ) from e


@router.get(
    "/me",
    response_model=schemas.UserProfile,
    status_code=status.HTTP_200_OK,
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다. 성공 시 사용자 프로필 정보를 반환합니다.",
)
async def get_my_profile(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
) -> models.User:
    """
    현재 로그인한 사용자의 프로필 정보를 조회
    """
    return current_user


# @router.get(
#     "/{user_id}",
#     response_model=schemas.UserRead,
#     status_code=status.HTTP_200_OK,
#     summary="사용자 조회",
#     description="사용자 ID로 사용자를 조회합니다. 성공 시 사용자 정보를 반환합니다.",
# )
# async def handle_get_user(
#     db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
# ) -> models.User:
#     """
#     사용자 ID로 사용자를 조회합니다. 성공 시 사용자 정보를 반환합니다.

#     :param db_user: 사용자 모델 (의존성 주입을 통해 조회)
#     :return: 조회된 사용자 모델
#     """
#     return db_user


# @router.patch(
#     "/{user_id}",
#     response_model=schemas.UserRead,
#     status_code=status.HTTP_200_OK,
#     summary="사용자 정보 수정",
#     description="사용자 ID로 사용자의 정보를 수정합니다. 성공 시 수정된 사용자 정보를 반환합니다.",
# )
# async def handle_update_user(
#     db: Annotated[AsyncSession, Depends(get_async_db)],
#     db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
#     user_update: schemas.UserUpdate,
# ) -> models.User:
#     """
#     사용자 ID로 사용자의 정보를 수정합니다. 성공 시 수정된 사용자 정보를 반환합니다.

#     :param db: 비동기 데이터베이스 세션
#     :param db_user: 수정할 사용자 모델 (의존성을 통해 조회)
#     :param user_update: 사용자 업데이트 스키마
#     :return: 수정된 사용자 모델
#     """

#     # db에 commit을 해야 하므로 db를 인자로 받음
#     updated_user = await service.update_user_profile(
#         db=db, db_user=db_user, user_update=user_update
#     )
#     return updated_user


# @router.patch(
#     "/{user_id}/deactivate",
#     response_model=schemas.UserRead,
#     status_code=status.HTTP_200_OK,
#     summary="사용자 비활성화",
#     description="사용자 ID로 사용자를 비활성화합니다. 성공 시 비활성화된 사용자 정보를 반환합니다.",
# )
# async def handle_deactivate_user(
#     db: Annotated[AsyncSession, Depends(get_async_db)],
#     db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
# ) -> models.User:
#     """
#     사용자 ID로 사용자를 비활성화합니다. 성공 시 비활성화된 사용자 정보를 반환합니다.

#     :param db: 비동기 데이터베이스 세션
#     :param db_user: 비활성화할 사용자 모델 (의존성 주입을 통해 조회)
#     :return: 비활성화된 사용자 모델
#     """
#     deactivated_user = await service.deactivate_user(db=db, db_user=db_user)
#     return deactivated_user


# @router.delete(
#     "/{user_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="사용자 삭제",
#     description="사용자 ID로 사용자를 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.",
# )
# async def handle_delete_user(
#     db: Annotated[AsyncSession, Depends(get_async_db)],
#     db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
# ) -> None:
#     """
#     사용자 ID로 사용자를 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.

#     :param db_user: 삭제할 사용자 모델 (의존성 주입을 통해 조회)
#     :return: None
#     """
#     await service.delete_user(db=db, db_user=db_user)
#     return None


# @router.patch(
#     "/{user_id}/admin",
#     response_model=schemas.UserRead,
#     status_code=status.HTTP_200_OK,
#     summary="관리자 권한 업데이트",
#     description="사용자 ID로 사용자의 관리자 권한을 업데이트합니다. 성공 시 업데이트된 사용자 정보를 반환합니다.",
# )
# async def handle_update_admin_status(
#     db: Annotated[AsyncSession, Depends(get_async_db)],
#     db_user: Annotated[models.User, Depends(get_user_by_id_or_404)],
#     admin_update: schemas.UserUpdateAdmin,
# ) -> models.User:
#     """
#     사용자 ID로 사용자의 관리자 권한을 업데이트합니다. 성공 시 업데이트된 사용자 정보를 반환합니다.

#     :param db: 비동기 데이터베이스 세션
#     :param db_user: 관리자 권한을 업데이트할 사용자 모델 (의존성 주입을 통해 조회)
#     :param admin_update: 관리자 권한 업데이트 스키마
#     :return: 업데이트된 사용자 모델
#     """
#     updated_user = await service.update_admin_status(
#         db=db, db_user=db_user, is_admin=admin_update.is_admin
#     )
#     return updated_user


# @router.get(
#     "/",
#     response_model=list[schemas.UserRead],
#     status_code=status.HTTP_200_OK,
#     summary="모든 사용자 조회",
#     description="모든 사용자를 조회합니다. 성공 시 사용자 목록을 반환합니다.",
# )
# async def handle_get_all_users(
#     db: Annotated[AsyncSession, Depends(get_async_db)],
#     skip: int = Query(0, ge=0, description="건너뛸 사용자 수"),
#     limit: int = Query(100, ge=1, le=100, description="조회할 최대 사용자 수"),
# ) -> list[models.User]:
#     """
#     모든 사용자를 조회합니다. 성공 시 사용자 목록을 반환합니다.

#     :param db: 비동기 데이터베이스 세션
#     :param skip: 건너뛸 사용자 수 (기본값: 0)
#     :param limit: 조회할 최대 사용자 수 (기본값: 100, 최소 1, 최대 100)
#     :return: 사용자 모델 리스트
#     """
#     users = await service.get_all_users(db=db, skip=skip, limit=limit)
#     return users
