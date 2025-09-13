from datetime import datetime

from pydantic import ConfigDict, Field

from src.common.schemas import AppBaseModel
from src.users.schemas import UserProfilePublic


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

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
    )


class PostLikeWithUser(PostLikeRead):
    """
    사용자 정보가 포함된 좋아요 정보 스키마
    """

    user: UserProfilePublic = Field(..., description="좋아요를 누른 사용자 정보")


class PostLikeListResponse(AppBaseModel):
    """
    좋아요 목록 응답을 표현하는 모델
    좋아요 목록과 함께 페이지네이션 정보를 포함
    """

    likes: list[PostLikeWithUser] = Field(
        ...,
        description="좋아요 정보 리스트",
    )
    total_count: int = Field(
        ...,
        description="전체 좋아요 수",
        examples=[50, 120],
    )
    page: int = Field(
        ...,
        description="현재 페이지 번호",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        ...,
        description="페이지당 좋아요 수",
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


class LikeToggleResponse(AppBaseModel):
    """
    좋아요 토글 응답 스키마
    """

    liked: bool = Field(
        ...,
        description="좋아요 상태 (True: 좋아요 추가, False: 좋아요 제거)",
        examples=[True, False],
    )
    like: PostLikeRead | None = Field(
        None,
        description="좋아요 정보 (좋아요가 추가된 경우에만 포함)",
    )
    total_likes: int = Field(
        ...,
        description="현재 게시글의 총 좋아요 수",
        examples=[10, 25, 100],
    )
