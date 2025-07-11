from fastapi import APIRouter, Query, status

from src.db.session import DbSession
from src.posts import models, schemas, service
from src.posts.dependencies import AuthorOrAdminPost, ValidPost
from src.users.dependencies import AdminUser, SelfUser

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=schemas.PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 생성",
    description="새로운 게시글을 생성합니다. 성공 시 게시글 정보를 반환합니다.",
)
async def create_post(
    db: DbSession,
    current_user: SelfUser,
    post_in: schemas.PostCreate,
) -> models.Post:
    """
    새로운 게시글을 생성합니다. 성공 시 게시글 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param current_user: 현재 로그인한 사용자 모델
    :param post_in: 게시글 생성 스키마
    :return: 생성된 게시글 모델
    """
    created_post = await service.create_post(
        db=db, post_create=post_in, db_user=current_user
    )
    return created_post


@router.get(
    "/",
    response_model=schemas.PostListResponse,
    status_code=status.HTTP_200_OK,
    summary="게시글 목록 조회",
    description="게시글 목록을 조회합니다. 성공 시 게시글 목록을 반환합니다.",
)
async def handle_get_posts(
    db: DbSession,
    skip: int = Query(0, ge=0, description="건너뛸 게시글 수"),
    limit: int = Query(10, ge=1, le=100, description="조회할 최대 게시글 수"),
) -> schemas.PostListResponse:
    """
    게시글 목록을 조회합니다. 성공 시 게시글 목록과 총 게시글 수를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param skip: 건너뛸 게시글 수 (기본값: 0)
    :param limit: 조회할 최대 게시글 수 (기본값: 10, 최대 100)
    :return: 게시글 모델 리스트와 총 게시글 수
    """
    posts, total_count = await service.get_posts_with_total_count(
        db=db, skip=skip, limit=limit
    )

    total_count_int: int = int(total_count)  # 타입 명시

    return schemas.PostListResponse(
        posts=posts,
        total_count=total_count_int,
        page=skip // limit + 1,
        page_size=limit,
        has_next=total_count_int > (skip + limit),
    )


@router.get(
    "/{post_id}",
    response_model=schemas.PostRead,
    status_code=status.HTTP_200_OK,
    summary="게시글 조회",
    description="게시글을 ID로 조회합니다. 성공 시 게시글 정보를 반환합니다.",
)
async def handle_get_post(
    db: DbSession,
    db_post: ValidPost,
) -> models.Post:
    """
    게시글을 ID로 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 게시글 모델 (의존성 주입을 통해 조회)
    :return: 게시글 모델
    """
    db_post = await service.get_post_by_id(db=db, db_post=db_post)
    return db_post


@router.patch(
    "/{post_id}",
    response_model=schemas.PostRead,
    status_code=status.HTTP_200_OK,
    summary="게시글 업데이트",
    description="게시글을 업데이트합니다. 성공 시 업데이트된 게시글 정보를 반환합니다.",
)
async def handle_update_post(
    db: DbSession,
    db_post: AuthorOrAdminPost,
    post_in: schemas.PostUpdate,
) -> models.Post:
    """
    게시글을 업데이트합니다. 성공 시 업데이트된 게시글 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 게시글 모델 (작성자 또는 관리자 권한 확인용)
    :param post_in: 게시글 업데이트 스키마
    :return: 업데이트된 게시글 모델
    """
    updated_post = await service.update_post(
        db=db, db_post=db_post, post_update=post_in
    )
    return updated_post


@router.patch(
    "/{post_id}/deactivate",
    response_model=schemas.PostRead,
    status_code=status.HTTP_200_OK,
    summary="게시글 비활성화",
    description="게시글을 비활성화(soft delete)합니다. 성공 시 비활성화된 게시글 정보를 반환합니다.",
)
async def handle_deactivate_post(
    db: DbSession,
    db_post: AuthorOrAdminPost,
) -> models.Post:
    """
    게시글을 비활성화(soft delete)합니다. 성공 시 비활성화된 게시글 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 게시글 모델 (의존성 주입을 통해 조회)
    :return: 비활성화된 게시글 모델
    """
    deactivated_post = await service.deactivate_post(db=db, db_post=db_post)
    return deactivated_post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="게시글 삭제",
    description="게시글을 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.",
)
async def handle_delete_post(
    db: DbSession,
    db_post: ValidPost,
    _current_user: AdminUser,
) -> None:
    """
    게시글 ID로 게시글을 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 게시글 모델 (의존성 주입을 통해 조회)
    :param _current_user: 현재 로그인한 사용자 모델 (관리자 권한 확인용)
    :return: None
    """
    await service.delete_post(db=db, db_post=db_post)
