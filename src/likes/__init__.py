"""
좋아요 모듈

이 모듈은 게시글 좋아요 기능을 처리합니다.
사용자가 게시글에 좋아요를 누르거나 취소할 수 있는 기능을 제공합니다.
"""

from src.likes import crud, dependencies, models, router, schemas, service

__all__ = [
    "crud",
    "dependencies",
    "models",
    "router",
    "schemas",
    "service",
]
