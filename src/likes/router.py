from fastapi import APIRouter, Query, status

from src.db.session import DbSession
from src.likes import crud, schemas, service
from src.likes.dependencies import OwnerLike
from src.likes.models import PostLike
from src.posts.dependencies import ValidPost
from src.users.dependencies import SelfUser, ValidUser

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post(
    "/posts/{post_id}",
    response_model=schemas.PostLikeRead,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 좋아요",
    description="게시글에 좋아요를 추가합니다. 성공 시 좋아요 정보를 반환합니다.",
)
async def handle_create_like(
    db: DbSession,
    db_post: ValidPost,
    current_user: SelfUser,
) -> PostLike:
    """
    게시글에 좋아요를 추가합니다. 성공 시 좋아요 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 유효성 검사가 완료된 게시글 모델
    :param current_user: 현재 로그인한 사용자 모델
    :return: 생성된 좋아요 모델
    """
    created_like = await service.create_like(
        db=db, post_id=db_post.id, db_user=current_user
    )
    return created_like


@router.post(
    "/posts/{post_id}/toggle",
    response_model=schemas.LikeToggleResponse,
    status_code=status.HTTP_200_OK,
    summary="게시글 좋아요 토글",
    description="게시글 좋아요를 토글합니다. 있으면 삭제, 없으면 생성합니다.",
)
async def handle_toggle_like(
    db: DbSession,
    db_post: ValidPost,
    current_user: SelfUser,
) -> schemas.LikeToggleResponse:
    """
    게시글 좋아요를 토글합니다. 있으면 삭제, 없으면 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 유효성 검사가 완료된 게시글 모델
    :param current_user: 현재 로그인한 사용자 모델
    :return: 토글 결과 정보
    """
    like, created = await service.toggle_like(
        db=db, post_id=db_post.id, db_user=current_user
    )

    # 현재 게시글의 총 좋아요 수 조회
    total_likes = await crud.get_total_likes_count_by_post(db=db, post_id=db_post.id)

    return schemas.LikeToggleResponse(
        liked=created,
        like=like,
        total_likes=total_likes,
    )


@router.get(
    "/posts/{post_id}",
    response_model=schemas.PostLikeListResponse,
    status_code=status.HTTP_200_OK,
    summary="게시글 좋아요 목록 조회",
    description="특정 게시글의 좋아요 목록을 조회합니다. 성공 시 좋아요 목록을 반환합니다.",
)
async def handle_get_likes_by_post(
    db: DbSession,
    db_post: ValidPost,
    skip: int = Query(0, ge=0, description="건너뛸 좋아요 수"),
    limit: int = Query(10, ge=1, le=100, description="조회할 최대 좋아요 수"),
) -> schemas.PostLikeListResponse:
    """
    특정 게시글의 좋아요 목록을 조회합니다. 성공 시 좋아요 목록과 총 좋아요 수를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 유효성 검사가 완료된 게시글 모델
    :param skip: 건너뛸 좋아요 수 (기본값: 0)
    :param limit: 조회할 최대 좋아요 수 (기본값: 10, 최대 100)
    :return: 좋아요 목록과 페이지네이션 정보
    """
    likes, total_count = await service.get_likes_with_total_count_by_post(
        db=db, post_id=db_post.id, skip=skip, limit=limit
    )

    return schemas.PostLikeListResponse(
        likes=likes,
        total_count=total_count,
        page=skip // limit + 1,
        page_size=limit,
        has_next=total_count > (skip + limit),
    )


@router.get(
    "/users/{user_id}",
    response_model=schemas.PostLikeListResponse,
    status_code=status.HTTP_200_OK,
    summary="사용자 좋아요 목록 조회",
    description="특정 사용자가 누른 좋아요 목록을 조회합니다. 성공 시 좋아요 목록을 반환합니다.",
)
async def handle_get_likes_by_user(
    db: DbSession,
    db_user: ValidUser,
    skip: int = Query(0, ge=0, description="건너뛸 좋아요 수"),
    limit: int = Query(10, ge=1, le=100, description="조회할 최대 좋아요 수"),
) -> schemas.PostLikeListResponse:
    """
    특정 사용자가 누른 좋아요 목록을 조회합니다. 성공 시 좋아요 목록과 총 좋아요 수를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_user: 유효성 검사가 완료된 사용자 모델
    :param skip: 건너뛸 좋아요 수 (기본값: 0)
    :param limit: 조회할 최대 좋아요 수 (기본값: 10, 최대 100)
    :return: 좋아요 목록과 페이지네이션 정보
    """
    likes, total_count = await service.get_likes_with_total_count_by_user(
        db=db, user_id=db_user.id, skip=skip, limit=limit
    )

    return schemas.PostLikeListResponse(
        likes=likes,
        total_count=total_count,
        page=skip // limit + 1,
        page_size=limit,
        has_next=total_count > (skip + limit),
    )


@router.delete(
    "/posts/{post_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="좋아요 삭제",
    description="특정 게시글의 특정 사용자 좋아요를 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.",
)
async def handle_delete_like(
    db: DbSession,
    db_like: OwnerLike,
) -> None:
    """
    좋아요를 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_like: 소유자 권한이 확인된 좋아요 모델
    :return: None
    """
    await service.delete_like(db=db, db_like=db_like)


@router.get(
    "/posts/{post_id}/check",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="좋아요 상태 확인",
    description="현재 사용자가 특정 게시글에 좋아요를 눌렀는지 확인합니다.",
)
async def handle_check_like_status(
    db: DbSession,
    db_post: ValidPost,
    current_user: SelfUser,
) -> dict:
    """
    현재 사용자가 특정 게시글에 좋아요를 눌렀는지 확인합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 유효성 검사가 완료된 게시글 모델
    :param current_user: 현재 로그인한 사용자 모델
    :return: 좋아요 상태 정보
    """
    like = await service.get_like_by_post_and_user(
        db=db, post_id=db_post.id, user_id=current_user.id
    )

    # 총 좋아요 수도 함께 조회
    total_likes = await crud.get_total_likes_count_by_post(db=db, post_id=db_post.id)

    return {
        "liked": like is not None,
        "total_likes": total_likes,
        "like_created_at": like.created_at if like else None,
    }
