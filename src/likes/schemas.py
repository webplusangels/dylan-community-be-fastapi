from datetime import datetime

from pydantic import Field

from src.common.schemas import AppBaseModel


class PostLikeBase(AppBaseModel):
    """
    게시글 좋아요의 기본 속성을 정의하는 모델
    """

    post_id: str = Field(
        ...,
        description="좋아요한 게시글의 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    user_id: str = Field(
        ...,
        description="좋아요를 누른 사용자의 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class PostLikeRead(PostLikeBase):
    """
    게시글 좋아요 정보를 읽기 위한 스키마
    """

    created_at: datetime = Field(
        ...,
        description="좋아요 생성 시간 (ISO 8601 형식)",
        examples=["2023-10-01T12:00:00Z"],
    )
