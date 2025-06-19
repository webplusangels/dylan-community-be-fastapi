# 테스트 DB 설정 후에 주석 해제하여 통합 테스트를 실행할 수 있습니다.
# from datetime import datetime, timezone

# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession

# from src.auth import crud


# @pytest.mark.asyncio
# async def test_add_and_check_token_blocklist_integration(test_db: AsyncSession):
#     """
#     토큰 블락리스트 추가/확인 통합 테스트 (실제 DB 사용)
#     """
#     # Arrange
#     jti = "integration_test_jti"
#     expires_at = datetime.now(timezone.utc)

#     # Act - 토큰 블락리스트에 추가
#     await crud.add_token_to_blocklist(db=test_db, jti=jti, expires_at=expires_at)

#     # Assert - 토큰이 블락리스트에 있는지 확인
#     is_blocked = await crud.is_token_blocked(db=test_db, jti=jti)
#     assert is_blocked is True

#     # 없는 토큰은 블락되지 않음
#     is_not_blocked = await crud.is_token_blocked(db=test_db, jti="nonexistent_jti")
#     assert is_not_blocked is False
