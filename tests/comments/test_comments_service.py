from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.comments import models, schemas, service
from src.posts.models import Post
from src.users.models import User


@pytest.mark.asyncio
async def test_create_comment_service_success(mocker):
    """
    댓글 생성 서비스 로직 성공 테스트
    """
    mock_db = AsyncMock()

    @asynccontextmanager
    async def fake_begin():
        yield mock_db

    mock_db.begin = fake_begin

    comment_in = schemas.CommentCreate(post_id="p1", content="Nice post")
    db_user = User(id="u1")

    created = models.PostComment(
        id="c1", post_id="p1", user_id=db_user.id, content="Nice post"
    )

    mocker.patch("src.comments.crud.create_comment", return_value=created)
    mocker.patch("src.comments.service.get_post", return_value=Post(id="p1"))
    mocker.patch("src.comments.service.increment_comment_count", return_value=None)

    result = await service.create_comment(
        db=mock_db, comment_create=comment_in, db_user=db_user
    )

    assert result == created


@pytest.mark.asyncio
async def test_get_comment_by_id_service_not_found(mocker):
    """
    댓글 ID로 조회 시, 존재하지 않으면 404 예외 발생
    """
    mock_db = AsyncMock()
    mocker.patch("src.comments.crud.get_comment", return_value=None)

    with pytest.raises(HTTPException) as exc:
        await service.get_comment_by_id(db=mock_db, comment_id="does-not-exist")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_comments_with_total_count_by_post_success(mocker):
    """
    특정 게시글의 댓글 목록 및 총 개수 조회 서비스 로직 성공 테스트
    """
    mock_db = AsyncMock()
    comments_mock = [models.PostComment(id="c1"), models.PostComment(id="c2")]
    mocker.patch("src.comments.crud.get_comments", return_value=comments_mock)
    mocker.patch("src.comments.crud.get_total_comments_count", return_value=2)

    comments, total = await service.get_comments_with_total_count_by_post(
        db=mock_db, post_id="p1", skip=0, limit=10
    )

    assert comments == comments_mock
    assert total == 2


@pytest.mark.asyncio
async def test_update_comment_service_success(mocker):
    """
    댓글 수정 서비스 로직 성공 테스트
    """
    mock_db = AsyncMock()
    db_comment = models.PostComment(id="c1", content="old")
    update = schemas.CommentUpdate(content="new")
    updated = models.PostComment(id="c1", content="new")

    mocker.patch("src.comments.crud.update_comment", return_value=updated)

    result = await service.update_comment(
        db=mock_db, db_comment=db_comment, comment_update=update
    )

    assert result.content == updated.content


@pytest.mark.asyncio
async def test_update_comment_service_failure(mocker):
    """
    댓글 수정 서비스 로직 실패 테스트
    """
    mock_db = AsyncMock()
    db_comment = models.PostComment(id="c1", content="old")
    update = schemas.CommentUpdate(content="new")

    mocker.patch(
        "src.comments.crud.update_comment",
        side_effect=HTTPException(status_code=409, detail="err"),
    )

    with pytest.raises(HTTPException):
        await service.update_comment(
            db=mock_db, db_comment=db_comment, comment_update=update
        )


@pytest.mark.asyncio
async def test_deactivate_and_delete_comment_service(mocker):
    """
    댓글 비활성화 및 삭제 서비스 로직 테스트
    """
    mock_db = AsyncMock()

    @asynccontextmanager
    async def fake_begin():
        yield mock_db

    mock_db.begin = fake_begin

    db_comment = models.PostComment(id="c1", content="c")

    deactivated = models.PostComment(id="c1", is_active=False)
    mocker.patch("src.comments.crud.deactivate_comment", return_value=deactivated)
    mocker.patch("src.comments.service.decrement_comment_count", return_value=None)
    mocker.patch("src.comments.crud.delete_comment", return_value=True)

    result_deact = await service.deactivate_comment(db=mock_db, db_comment=db_comment)
    assert result_deact.is_active is False

    result_del = await service.delete_comment(db=mock_db, db_comment=db_comment)
    assert result_del is None
