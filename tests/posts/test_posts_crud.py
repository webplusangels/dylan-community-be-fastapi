import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts import crud
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostUpdate
from src.users.models import User


@pytest.mark.asyncio
async def test_create_post(db_session: AsyncSession, test_user: User):
    """
    게시글 생성 테스트
    """
    # Arrange
    post_in = PostCreate(title="Test Post Title", content="Test Post Content")

    # Act
    created_post = await crud.create_post(
        db=db_session, post_in=post_in, user_id=str(test_user.id)
    )

    # Assert
    assert created_post.id is not None
    assert created_post.title == post_in.title
    assert created_post.content == post_in.content
    assert created_post.user_id == str(test_user.id)
    assert created_post.author.id == str(test_user.id)


@pytest.mark.asyncio
async def test_get_post(db_session: AsyncSession, test_post: Post):
    """
    게시글 조회 테스트
    """
    # Act
    fetched_post = await crud.get_post(db=db_session, post_id=str(test_post.id))

    # Assert
    assert fetched_post is not None
    assert fetched_post.id == str(test_post.id)
    assert fetched_post.title == test_post.title
    assert fetched_post.author.id == test_post.author.id


@pytest.mark.asyncio
async def test_get_posts(db_session: AsyncSession, test_user: User):
    """
    게시글 목록 조회 테스트
    """
    # Arrange
    for i in range(5):
        post_in = PostCreate(title=f"Post {i}", content=f"Content {i}")
        await crud.create_post(
            db=db_session, post_in=post_in, user_id=str(test_user.id)
        )

    # Act
    posts = await crud.get_posts(db=db_session, skip=0, limit=3)

    # Assert
    assert len(posts) == 3
    assert posts[0].title == "Post 4"  # 최신 게시글부터 정렬


@pytest.mark.asyncio
async def test_update_post(db_session: AsyncSession, test_post: Post):
    """
    게시글 업데이트 테스트
    """
    # Arrange
    update_data = PostUpdate(title="Updated Title", content="Updated Content")

    # Act
    updated_post = await crud.update_post(
        db=db_session, db_post=test_post, post_update=update_data
    )

    # Assert
    assert updated_post.title == "Updated Title"
    assert updated_post.content == "Updated Content"


@pytest.mark.asyncio
async def test_deactivate_post(db_session: AsyncSession, test_post: Post):
    """
    게시글 비활성화 테스트
    """
    # Act
    deactivated_post = await crud.deactivate_post(db=db_session, db_post=test_post)

    # Assert
    assert deactivated_post.deleted_at is not None
    assert deactivated_post.is_active is False


@pytest.mark.asyncio
async def test_delete_post(db_session: AsyncSession, test_post: Post):
    """
    게시글 삭제 테스트
    """
    # Arrange
    post_id = str(test_post.id)

    # Act: 게시글 삭제
    await crud.delete_post(db=db_session, db_post=test_post)

    # Assert: 게시글이 데이터베이스에서 삭제되었는지 확인
    stmt = select(Post).where(Post.id == post_id)
    result = await db_session.execute(stmt)
    fetched_post = result.scalar_one_or_none()
    assert fetched_post is None, "게시글이 데이터베이스에서 삭제되지 않았습니다."


@pytest.mark.asyncio
async def test_increment_post_views(db_session: AsyncSession, test_post: Post):
    """
    게시글 조회수 증가 테스트
    """
    # Arrange
    initial_views = test_post.views

    # Act
    incremented_post = await crud.increment_post_views(db=db_session, db_post=test_post)

    # Assert
    assert incremented_post.views == initial_views + 1


@pytest.mark.asyncio
async def test_get_total_post_count(db_session: AsyncSession, test_user: User):
    """
    전체 게시글 수 조회 테스트
    """
    # Arrange
    initial_count = await crud.get_total_post_count(db=db_session)

    # 게시글 3개 추가
    for i in range(3):
        post_in = PostCreate(
            title=f"Count Test Post {i}",
            content="Content",
        )
        await crud.create_post(
            db=db_session, post_in=post_in, user_id=str(test_user.id)
        )

    # Act
    # 추가 후 전체 게시글 수 확인
    new_count = await crud.get_total_post_count(db=db_session)

    # Assert
    assert new_count == initial_count + 3


@pytest.mark.asyncio
async def test_search_posts(db_session: AsyncSession, test_user: User):
    """
    게시글 검색 테스트
    """
    # Arrange
    # 검색용 테스트 게시글 생성
    search_keyword = "SearchKeyword"
    for i in range(5):
        title = f"Post {i}"
        content = f"Content {i}"
        if i % 2 == 0:
            title += f" {search_keyword}"  # 짝수 인덱스 게시글 제목에 키워드 추가
        else:
            content += f" {search_keyword}"  # 홀수 인덱스 게시글 내용에 키워드 추가

        post_in = PostCreate(title=title, content=content)
        await crud.create_post(
            db=db_session, post_in=post_in, user_id=str(test_user.id)
        )

    # Act
    # 키워드로 검색
    searched_posts = await crud.search_posts(
        db=db_session, query=search_keyword, limit=5
    )

    # Assert
    assert len(searched_posts) == 5
    for post in searched_posts:
        assert search_keyword in post.title or search_keyword in post.content, (
            f"Keyword not found in post {post.id}"
        )

    # 검색 결과가 없는 경우 확인
    no_result_posts = await crud.search_posts(db=db_session, query="NonExistentKeyword")
    assert len(no_result_posts) == 0


@pytest.mark.asyncio
async def test_get_post_deactivated(db_session: AsyncSession, test_post: Post):
    """
    비활성화된 게시글 조회 테스트
    """
    # Act
    deactivated_post = await crud.deactivate_post(db=db_session, db_post=test_post)

    # Assert
    assert deactivated_post.is_active is False
    fetched_post = await crud.get_post(db=db_session, post_id=str(test_post.id))
    assert fetched_post is None


@pytest.mark.asyncio
async def test_get_posts_excludes_deactivated(
    db_session: AsyncSession, test_user: User
):
    """
    비활성화된 게시글이 목록에서 제외되는지 확인하는 테스트
    """
    # Arrange
    # 활성화된 게시글 2개 생성
    post1 = await crud.create_post(
        db=db_session,
        post_in=PostCreate(title="Active Post 1", content="Content 1"),
        user_id=str(test_user.id),
    )
    post2 = await crud.create_post(
        db=db_session,
        post_in=PostCreate(title="Active Post 2", content="Content 2"),
        user_id=str(test_user.id),
    )

    # 비활성화된 게시글 1개 생성
    deactivated_post = await crud.create_post(
        db=db_session,
        post_in=PostCreate(title="Deactivated Post", content="Content 3"),
        user_id=str(test_user.id),
    )

    # Act
    await crud.deactivate_post(db=db_session, db_post=deactivated_post)

    # Assert
    # 게시글 목록 조회 시 비활성화된 게시글이 제외되는지 확인
    posts = await crud.get_posts(db=db_session, skip=0, limit=10)
    assert len(posts) == 2  # 활성화된 게시글만 조회되어야 함
    assert all(post.is_active is True for post in posts)
    assert post1 in posts
    assert post2 in posts
    assert deactivated_post not in posts
