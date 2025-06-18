# 옮겨온 테스트 코드 (임시 주석 처리됨)
# @pytest.mark.asyncio
# async def test_authenticate_user_success(mocker):
#     """
#     사용자 인증 성공 테스트
#     """
#     # Arrange
#     mock_db = AsyncMock()
#     test_user = models.User(
#         email="test@example.com",
#         is_active=True,
#     )

#     mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
#     mocker.patch("src.users.service.verify_password", return_value=True)

#     # Act
#     authenticated_user = await service.authenticate_user(
#         db=mock_db, email=test_user.email, password="plainpassword123"
#     )

#     # Assert
#     assert authenticated_user is not None
#     assert authenticated_user.email == test_user.email


# @pytest.mark.asyncio
# async def test_authenticate_user_failure_wrong_password(mocker):
#     """
#     사용자 인증 실패 테스트(잘못된 비밀번호)
#     """
#     # Arrange
#     mock_db = AsyncMock()
#     test_user = models.User(
#         email="test@example.com",
#         hashed_password=hash_password("plainpassword123"),
#         is_active=True,
#     )

#     mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
#     mocker.patch("src.users.service.verify_password", return_value=False)

#     # Act
#     authenticated_user = await service.authenticate_user(
#         db=mock_db, email=test_user.email, password="wrongpassword123"
#     )

#     # Assert
#     assert authenticated_user is None


# @pytest.mark.asyncio
# async def test_authenticate_user_failure_inactive_user(mocker):
#     """
#     사용자 인증 실패 테스트(비활성화된 사용자)
#     """
#     # Arrange
#     mock_db = AsyncMock()
#     test_user = models.User(
#         email="test@example.com",
#         hashed_password=hash_password("plainpassword123"),
#         is_active=False,  # 비활성화된 사용자
#     )

#     mocker.patch("src.users.crud.get_user_by_email", return_value=test_user)
#     mocker.patch("src.users.service.verify_password", return_value=True)

#     # Act & Assert
#     with pytest.raises(HTTPException) as exc_info:
#         await service.authenticate_user(
#             db=mock_db, email=test_user.email, password="plainpassword123"
#         )

#     assert exc_info.value.status_code == 403
#     assert exc_info.value.detail == "사용자가 비활성화되었습니다."


# @pytest.mark.asyncio
# async def test_authenticate_user_failure_user_not_found(mocker):
#     """
#     사용자 인증 실패 테스트(사용자 없음)
#     """
#     # Arrange
#     mock_db = AsyncMock()
#     test_user = models.User(
#         id="uuid",
#         email="test@example.com",
#         hashed_password=hash_password("plainpassword123"),
#     )

#     mocker.patch("src.users.crud.get_user_by_email", return_value=None)

#     # Act
#     authenticated_user = await service.authenticate_user(
#         db=mock_db, email=test_user.email, password="plainpassword123"
#     )

#     # Assert
#     assert authenticated_user is None
