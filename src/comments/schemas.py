from datetime import datetime

from pydantic import ConfigDict, Field

from src.common.schemas import AppBaseModel
from src.users.schemas import UserProfilePublic


class CommentBase(AppBaseModel):
    """
    댓글의 기본 속성을 정의하는 모델
    다른 스키마들이 상속받아 사용할 수 있는 클래스
    """

    content: str = Field(
        ...,
        min_length=2,
        description="댓글 내용 (최소 2자)",
        examples=[
            "이 게시글 정말 유익하네요!",
            "좋은 정보 감사합니다.",
        ],
    )


class CommentCreate(CommentBase):
    """
    댓글 생성을 위한 스키마
    """

    post_id: str = Field(
        ...,
        description="댓글이 작성된 게시글 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class CommentUpdate(AppBaseModel):
    """
    댓글 업데이트를 위한 스키마
    """

    content: str = Field(
        ...,
        min_length=2,
        description="수정된 댓글 내용 (최소 2자)",
        examples=["수정된 댓글 내용입니다."],
    )


class CommentRead(CommentBase):
    """
    댓글 읽기를 위한 스키마
    """

    id: str = Field(
        ..., description="댓글 ID", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: datetime = Field(
        ..., description="댓글 생성 시간", examples=["2023-10-01T12:00:00Z"]
    )
    updated_at: datetime = Field(
        ..., description="댓글 수정 시간", examples=["2023-10-01T12:00:00Z"]
    )
    is_active: bool = Field(..., description="댓글 활성화 여부", examples=[True, False])

    author: UserProfilePublic = Field(
        ...,
        description="댓글 작성자 정보",
        examples=[
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "dylan_dev",
                "profile_image_path": "https://example.com/images/profile.jpg",
            }
        ],
    )

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
    )


class CommentListResponse(AppBaseModel):
    """
    댓글 목록 응답 스키마
    """

    comments: list[CommentRead] = Field(
        ...,
        description="댓글 목록",
    )
    total_count: int = Field(
        ...,
        description="전체 댓글 수",
        examples=[100],
    )
    page: int = Field(
        ...,
        description="현재 페이지 번호",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        ...,
        description="페이지당 댓글 수",
        examples=[10, 20, 50],
    )
    has_next: bool = Field(
        ...,
        description="다음 페이지가 있는지 여부",
        examples=[True, False],
    )

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
    )
