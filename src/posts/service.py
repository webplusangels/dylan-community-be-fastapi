from typing import Sequence, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.posts import crud, models, schemas
from src.users.models import User


async def create_post(
    db: AsyncSession, post_create: schemas.PostCreate, db_user: User
) -> models.Post:
    """
    게시글을 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_create: 게시글 생성 스키마
    :param db_user: 게시글 작성자 모델
    :return: 생성된 게시글 모델
    """
    created_post = await crud.create_post(
        db=db, post_in=post_create, user_id=db_user.id
    )

    return created_post


async def get_post_by_id(db: AsyncSession, db_post: models.Post) -> models.Post:
    """
    게시글을 ID로 조회합니다. 조회수를 1 증가시킵니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 데이터베이스에서 조회된 게시글 모델
    :return: 게시글 모델
    """
    await crud.increment_post_views(db=db, db_post=db_post)
    await db.refresh(
        db_post
    )  # Race Condition 방지 -> 게시글 조회로 유효한지 확인 후 조회수 증가
    return db_post


async def get_posts_with_total_count(
    db: AsyncSession, skip: int = 0, limit: int = 10
) -> Tuple[Sequence[models.Post], int]:
    """
    게시글 목록을 조회하고, 총 게시글 수를 반환합니다.

    :param db: 비동기 데이터베이스 세션
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 게시글 수 (페이징)
    :return: 게시글 모델 리스트, 총 게시글 수
    """
    posts = await crud.get_posts(db=db, skip=skip, limit=limit)
    total_count = await crud.get_total_post_count(db=db)
    return posts, total_count


async def update_post(
    db: AsyncSession,
    db_post: models.Post,
    post_update: schemas.PostUpdate,
) -> models.Post:
    """
    게시글을 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 데이터베이스에서 조회된 게시글 모델
    :param post_update: 게시글 업데이트 스키마
    :return: 업데이트된 게시글 모델
    """
    updated_post = await crud.update_post(
        db=db, db_post=db_post, post_update=post_update
    )
    return updated_post


async def deactivate_post(
    db: AsyncSession,
    db_post: models.Post,
) -> models.Post:
    """
    게시글을 비활성화(soft delete)합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 데이터베이스에서 조회된 게시글 모델
    :return: 비활성화된 게시글 모델
    """
    deactivated_post = await crud.deactivate_post(db=db, db_post=db_post)
    return deactivated_post


async def delete_post(
    db: AsyncSession,
    db_post: models.Post,
) -> None:
    """
    게시글을 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 데이터베이스에서 조회된 게시글 모델
    :return: 삭제된 게시글 모델
    """
    await crud.delete_post(db=db, db_post=db_post)
    return None


async def search_posts(
    db: AsyncSession,
    query: str,
    limit: int = 10,
) -> Sequence[models.Post]:
    """
    게시글 제목 또는 내용에서 키워드로 검색합니다.

    :param db: 비동기 데이터베이스 세션
    :param query: 검색할 키워드
    :param limit: 조회할 게시글 수 (페이징)
    :return: 검색된 게시글 모델 리스트
    """
    posts = await crud.search_posts(db=db, query=query, limit=limit)
    return posts


# async def toggle_post_like(
#     db: AsyncSession,
#     db_post: models.Post,
#     current_user: User,
# ) -> models.Post:
#     """
#     게시글에 좋아요를 토글합니다. 좋아요가 없으면 추가하고, 있으면 제거합니다.

#     :param db: 비동기 데이터베이스 세션
#     :param db_post: 데이터베이스에서 조회된 게시글 모델
#     :param current_user: 현재 사용자 모델
#     :return: 업데이트된 게시글 모델
#     """
#     updated_post = await crud.toggle_post_like(
#         db=db, db_post=db_post, user_id=current_user.id
#     )
#     return updated_post
