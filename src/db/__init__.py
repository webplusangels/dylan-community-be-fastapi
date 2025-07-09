# flake8: noqa
# isort: skip_file

# 모든 모델을 Base에 등록하기 위해 import합니다.
# Alembic 마이그레이션을 위해 필요합니다.
from src.users.models import User
from src.posts.models import Post
from src.comments.models import PostComment
from src.likes.models import PostLike
