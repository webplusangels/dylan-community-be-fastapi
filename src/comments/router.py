from fastapi import APIRouter, status

from src.comments import models, schemas, service
from src.comments.dependencies import AuthorOrAdminComment, ValidComment
from src.db.session import DbSession
from src.users.dependencies import AdminUser, SelfUser

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/",
    response_model=schemas.CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="댓글 생성",
    description="새로운 댓글을 생성합니다. 성공 시 댓글 정보를 반환합니다.",
)
async def handle_create_comment(
    db: DbSession,
    current_user: SelfUser,
    comment_in: schemas.CommentCreate,
) -> models.PostComment:
    """
    새로운 댓글을 생성합니다. 성공 시 댓글 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param current_user: 현재 로그인한 사용자 모델
    :param comment_in: 댓글 생성 스키마
    :return: 생성된 댓글 모델
    """
    created_comment = await service.create_comment(
        db=db, comment_create=comment_in, db_user=current_user
    )
    return created_comment


@router.get(
    "/{comment_id}",
    response_model=schemas.CommentRead,
    status_code=status.HTTP_200_OK,
    summary="댓글 조회",
    description="댓글 ID로 댓글을 조회합니다. 성공 시 댓글 정보를 반환합니다.",
)
async def handle_get_comment(
    db_comment: ValidComment,
) -> models.PostComment:
    """
    댓글 ID로 댓글을 조회합니다. 성공 시 댓글 정보를 반환합니다.

    :param db_comment: 조회할 댓글 모델 (유효성 검사 포함)
    :return: 조회된 댓글 모델
    """
    return db_comment


@router.patch(
    "/{comment_id}",
    response_model=schemas.CommentRead,
    status_code=status.HTTP_200_OK,
    summary="댓글 수정",
    description="댓글 ID로 댓글을 수정합니다. 성공 시 수정된 댓글 정보를 반환합니다.",
)
async def handle_update_comment(
    db: DbSession,
    db_comment: AuthorOrAdminComment,
    comment_in: schemas.CommentUpdate,
) -> models.PostComment:
    """
    댓글을 업데이트합니다. 성공 시 수정된 댓글 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 수정할 댓글 모델 (작성자 또는 관리자 권한 확인)
    :param comment_in: 댓글 수정 스키마
    :return: 수정된 댓글 모델
    """
    updated_comment = await service.update_comment(
        db=db, db_comment=db_comment, comment_update=comment_in
    )
    return updated_comment


@router.patch(
    "/{comment_id}/deactivate",
    response_model=schemas.CommentRead,
    status_code=status.HTTP_200_OK,
    summary="댓글 비활성화",
    description="댓글 ID로 댓글을 비활성화합니다. 성공 시 비활성화된 댓글 정보를 반환합니다.",
)
async def handle_deactivate_comment(
    db: DbSession,
    db_comment: AuthorOrAdminComment,
) -> models.PostComment:
    """
    댓글을 비활성화(삭제)합니다. 성공 시 비활성화된 댓글 정보를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 비활성화할 댓글 모델 (작성자 또는 관리자 권한 확인)
    :return: 비활성화된 댓글 모델
    """
    deactivated_comment = await service.deactivate_comment(db=db, db_comment=db_comment)
    return deactivated_comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="댓글 삭제",
    description="댓글 ID로 댓글을 영구 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.",
)
async def handle_delete_comment(
    db: DbSession,
    db_comment: ValidComment,
    _current_user: AdminUser,
) -> None:
    """
    댓글을 영구 삭제합니다. 성공 시 204 No Content 응답을 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_comment: 삭제할 댓글 모델
    :param _current_user: 현재 로그인한 관리자 사용자 모델 (권한 확인용)
    :return: None
    """
    await service.delete_comment(db=db, db_comment=db_comment)
