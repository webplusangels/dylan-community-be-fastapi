from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.crud import add_and_commit, commit_and_refresh, delete_and_commit
from src.likes.models import PostLike
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostUpdate


async def create_post(db: AsyncSession, post_in: PostCreate, user_id: str) -> Post:
    """
    새로운 게시글을 생성합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_in: 게시글 생성 스키마
    :param user_id: 게시글 작성자의 사용자 ID (서비스 계층에서 인증해 제공)
    :return: 생성된 게시글 모델
    :raises HTTPException: 게시글 생성 중 오류 발생 시
    """
    db_post = Post(**post_in.model_dump(), user_id=user_id)

    try:
        return await add_and_commit(db, db_post)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="게시글 생성 중 오류가 발생했습니다. 존재하지 않는 사용자 ID이거나 리소스 충돌이 발생했을 수 있습니다.",
        ) from err


async def get_post(db: AsyncSession, post_id: str) -> Post | None:
    """
    게시글을 ID로 조회합니다. (작성자 정보 포함)

    :param db: 비동기 데이터베이스 세션
    :param post_id: 조회할 게시글 ID
    :return: 게시글 모델 또는 None
    """
    stmt = Post.with_author(Post.active_query()).where(Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 10) -> Sequence[Post]:
    """
    게시글 목록을 조회합니다. (작성자 정보 포함)

    :param db: 비동기 데이터베이스 세션
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 게시글 수 (페이징)
    :return: 게시글 모델 리스트
    """
    stmt = (
        Post.with_author(Post.active_query())
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_total_post_count(db: AsyncSession) -> int:
    """
    활성화된 전체 게시글 수를 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :return: 전체 게시글 수
    """
    stmt = select(func.count()).select_from(Post.active_query().subquery())
    result = await db.execute(stmt)
    return result.scalar_one() or 0


async def search_posts(
    db: AsyncSession, query: str, skip: int = 0, limit: int = 10
) -> Sequence[Post]:
    """
    게시글 제목 또는 내용에서 키워드로 검색합니다.

    :param db: 비동기 데이터베이스 세션
    :param query: 검색할 키워드
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 게시글 수 (페이징)
    :return: 검색된 게시글 모델 리스트
    """
    search_filter = or_(
        Post.title.ilike(f"%{query}%"), Post.content.ilike(f"%{query}%")
    )
    stmt = (
        Post.with_author(Post.active_query())
        .filter(search_filter)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_posts_by_user(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10
) -> Sequence[Post]:
    """
    특정 사용자의 게시글 목록을 조회합니다.

    :param db: 비동기 데이터베이스 세션
    :param user_id: 조회할 사용자의 ID
    :param skip: 조회 시작 위치 (페이징)
    :param limit: 조회할 게시글 수 (페이징)
    :return: 게시글 모델 리스트
    """
    stmt = (
        Post.active_query()
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_post(db: AsyncSession, db_post: Post, post_update: PostUpdate) -> Post:
    """
    게시글을 업데이트합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 업데이트할 게시글 모델 (DB에서 조회된 상태여야 함)
    :param post_in: 게시글 업데이트 스키마
    :return: 업데이트된 게시글 모델
    :raises HTTPException: 게시글이 존재하지 않거나 업데이트 중 오류 발생 시
    """
    update_data = post_update.model_dump(mode="json", exclude_unset=True)
    if not update_data:
        return db_post

    for key, value in update_data.items():
        setattr(db_post, key, value)

    try:
        return await commit_and_refresh(db, db_post)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="게시글 업데이트 중 오류가 발생했습니다. 리소스 충돌이 발생했을 수 있습니다.",
        ) from err


async def deactivate_post(db: AsyncSession, db_post: Post) -> Post:
    """
    게시글을 비활성화(삭제)합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 비활성화할 게시글 모델 (DB에서 조회된 상태여야 함)
    :return: 비활성화된 게시글 모델
    :raises HTTPException: 게시글이 존재하지 않거나 삭제 중 오류 발생 시
    """
    if db_post.deleted_at is None:
        db_post.deleted_at = datetime.now(timezone.utc)
        db_post.is_active = False

        try:
            return await commit_and_refresh(db, db_post)
        except IntegrityError as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="게시글 비활성화 중 오류가 발생했습니다. 리소스 충돌이 발생했을 수 있습니다.",
            ) from err
    return db_post


async def delete_post(db: AsyncSession, db_post: Post) -> bool:
    """
    게시글을 영구 삭제합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 삭제할 게시글 모델 (DB에서 조회된 상태여야 함)
    :raises HTTPException: 게시글이 존재하지 않거나 삭제 중 오류 발생 시
    """
    try:
        return await delete_and_commit(db, db_post)
    except IntegrityError as err:
        await db.rollback()  # 트랜잭션 롤백
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="게시글 삭제 중 오류가 발생했습니다.",
        ) from err


async def increment_post_views(db: AsyncSession, db_post: Post) -> Post:
    """
    게시글 조회수를 원자적으로 증가시킵니다.
    데이터베이스 수준에서 직접 값을 증가시켜 동시성 문제를 방지합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 조회수를 증가시킬 게시글 모델
    :return: 조회수가 증가된 게시글 모델
    """
    stmt = (
        update(Post)
        .where(Post.id == db_post.id)
        .values(views=Post.views + 1)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    return await commit_and_refresh(db, db_post)


async def get_like_by_user(
    db: AsyncSession, post_id: str, user_id: str
) -> PostLike | None:
    """
    사용자가 특정 게시글에 좋아요를 눌렀는지 확인합니다.

    :param db: 비동기 데이터베이스 세션
    :param post_id: 게시글 ID
    :param user_id: 사용자 ID
    :return: PostLike 모델 또는 None
    """
    stmt = select(PostLike).where(
        PostLike.post_id == post_id, PostLike.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_like(db: AsyncSession, db_post: Post, user_id: str) -> Post:
    """
    게시글에 좋아요를 추가하고, 게시글의 좋아요 수를 원자적으로 증가시킵니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 좋아요를 추가할 게시글 모델
    :param user_id: 좋아요를 누른 사용자 ID
    :return: 업데이트된 게시글 모델
    """
    like = PostLike(post_id=db_post.id, user_id=user_id)
    db.add(like)

    stmt = (
        update(Post)
        .where(Post.id == db_post.id)
        .values(likes=Post.likes + 1)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    return await commit_and_refresh(db, db_post)


async def remove_like(db: AsyncSession, db_post: Post, like: PostLike) -> Post:
    """
    게시글 좋아요를 취소하고, 게시글의 좋아요 수를 원자적으로 감소시킵니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 좋아요를 취소할 게시글 모델
    :param like: 삭제할 PostLike 모델
    :return: 업데이트된 게시글 모델
    """
    stmt = (
        update(Post)
        .where(Post.id == db_post.id, Post.likes > 0)
        .values(likes=Post.likes - 1)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    await db.delete(like)
    return await commit_and_refresh(db, db_post)


async def toggle_like(db: AsyncSession, db_post: Post, user_id: str) -> Post:
    """
    게시글 좋아요를 토글합니다. 좋아요가 없으면 추가하고, 있으면 취소합니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 좋아요를 토글할 게시글 모델
    :param user_id: 사용자 ID
    :return: 업데이트된 게시글 모델
    """
    like = await get_like_by_user(db, db_post.id, user_id)

    if like:
        return await remove_like(db, db_post, like)
    else:
        return await add_like(db, db_post, user_id)


async def increment_comment_count(db: AsyncSession, db_post: Post) -> Post:
    """
    게시글 댓글 수를 원자적으로 증가시킵니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 댓글 수를 증가시킬 게시글 모델
    :return: 업데이트된 게시글 모델
    """
    stmt = (
        update(Post)
        .where(Post.id == db_post.id)
        .values(comments_count=Post.comments_count + 1)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    return await commit_and_refresh(db, db_post)


async def decrement_comment_count(db: AsyncSession, db_post: Post) -> Post:
    """
    게시글 댓글 수를 원자적으로 감소시킵니다.

    :param db: 비동기 데이터베이스 세션
    :param db_post: 댓글 수를 감소시킬 게시글 모델
    :return: 업데이트된 게시글 모델
    """
    stmt = (
        update(Post)
        .where(Post.id == db_post.id, Post.comments_count > 0)
        .values(comments_count=Post.comments_count - 1)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    return await commit_and_refresh(db, db_post)
