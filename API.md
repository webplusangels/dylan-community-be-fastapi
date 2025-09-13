# Dylan Community API 명세서

## 개요

Dylan Community API는 낯가리는 사람들을 위한 커뮤니티 플랫폼의 백엔드 API입니다. 이 API는 사용자 인증, 게시글 관리, 댓글, 좋아요 기능을 제공합니다.

## Base URL

```
http://localhost:8000/api/v1
```

## 인증

대부분의 API 엔드포인트는 JWT Bearer 토큰을 통한 인증이 필요합니다.

```http
Authorization: Bearer <your-jwt-token>
```

## 응답 형식

모든 API 응답은 JSON 형식을 사용합니다.

### 성공 응답

- 2xx 상태 코드와 함께 요청된 데이터를 반환합니다.

### 오류 응답

- 4xx/5xx 상태 코드와 함께 오류 정보를 반환합니다.

```json
{
  "detail": "오류 메시지"
}
```

---

## 1. 인증 (Auth)

### 1.1 사용자 로그인

**POST** `/auth/login`

사용자 이메일과 비밀번호로 로그인합니다.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Response (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Errors

- **401 Unauthorized**: 잘못된 이메일 또는 비밀번호
- **422 Unprocessable Entity**: 유효하지 않은 요청 데이터

---

### 1.2 사용자 로그아웃

**POST** `/auth/logout`

현재 사용자를 로그아웃하고 토큰을 무효화합니다.

#### Headers

```
Authorization: Bearer <token>
```

#### Response (200)

```json
{
  "message": "로그아웃되었습니다."
}
```

---

### 1.3 토큰 갱신

**POST** `/auth/refresh`

기존 토큰을 갱신합니다.

#### Headers

```
Authorization: Bearer <token>
```

#### Response (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## 2. 사용자 (Users)

### 2.1 사용자 생성

**POST** `/users/`

새로운 사용자를 생성합니다.

#### Request Body

```json
{
  "email": "newuser@example.com",
  "username": "newuser123",
  "password": "securepassword123",
  "profile_image_path": "https://example.com/images/profile.jpg"
}
```

#### Response (201)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newuser@example.com",
  "username": "newuser123",
  "profile_image_path": "https://example.com/images/profile.jpg",
  "is_active": true,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:00:00Z"
}
```

#### Errors

- **409 Conflict**: 이미 존재하는 이메일 또는 사용자명
- **422 Unprocessable Entity**: 유효하지 않은 요청 데이터

---

### 2.2 사용자 목록 조회

**GET** `/users/`

사용자 목록을 조회합니다. (관리자 권한 필요)

#### Query Parameters

- `skip` (int, optional): 건너뛸 사용자 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 사용자 수 (기본값: 10, 최대: 100)

#### Headers

```
Authorization: Bearer <admin-token>
```

#### Response (200)

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "user123",
    "profile_image_path": "https://example.com/images/profile.jpg",
    "is_active": true,
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
  }
]
```

---

### 2.3 특정 사용자 조회

**GET** `/users/{user_id}`

특정 사용자의 정보를 조회합니다.

#### Path Parameters

- `user_id` (string): 사용자 ID

#### Response (200)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "user123",
  "profile_image_path": "https://example.com/images/profile.jpg",
  "is_active": true,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:00:00Z"
}
```

#### Errors

- **404 Not Found**: 사용자를 찾을 수 없음

---

### 2.4 사용자 프로필 업데이트

**PATCH** `/users/{user_id}`

사용자의 프로필 정보를 업데이트합니다. (본인 또는 관리자만 가능)

#### Path Parameters

- `user_id` (string): 사용자 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Request Body

```json
{
  "username": "updated_username",
  "profile_image_path": "https://example.com/images/new_profile.jpg"
}
```

#### Response (200)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "updated_username",
  "profile_image_path": "https://example.com/images/new_profile.jpg",
  "is_active": true,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T13:00:00Z"
}
```

---

### 2.5 사용자 비활성화

**PATCH** `/users/{user_id}/deactivate`

사용자를 비활성화합니다. (본인 또는 관리자만 가능)

#### Path Parameters

- `user_id` (string): 사용자 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (200)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "user123",
  "profile_image_path": "https://example.com/images/profile.jpg",
  "is_active": false,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T14:00:00Z"
}
```

---

### 2.6 사용자 삭제

**DELETE** `/users/{user_id}`

사용자를 삭제합니다. (관리자 권한 필요)

#### Path Parameters

- `user_id` (string): 사용자 ID

#### Headers

```
Authorization: Bearer <admin-token>
```

#### Response (204)

No content

---

## 3. 게시글 (Posts)

### 3.1 게시글 생성

**POST** `/posts/`

새로운 게시글을 생성합니다.

#### Headers

```
Authorization: Bearer <token>
```

#### Request Body

```json
{
  "title": "첫 번째 게시글",
  "content": "이것은 첫 번째 게시글의 내용입니다."
}
```

#### Response (201)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "첫 번째 게시글",
  "content": "이것은 첫 번째 게시글의 내용입니다.",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "views": 0,
  "likes": 0,
  "is_active": true,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "author123",
    "profile_image_path": "https://example.com/images/author.jpg"
  }
}
```

---

### 3.2 게시글 목록 조회

**GET** `/posts/`

게시글 목록을 조회합니다.

#### Query Parameters

- `skip` (int, optional): 건너뛸 게시글 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 게시글 수 (기본값: 10, 최대: 100)

#### Response (200)

```json
{
  "posts": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "첫 번째 게시글",
      "content": "이것은 첫 번째 게시글의 내용입니다.",
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "views": 10,
      "likes": 5,
      "is_active": true,
      "created_at": "2023-10-01T12:00:00Z",
      "updated_at": "2023-10-01T12:00:00Z",
      "author": {
        "id": "456e7890-e89b-12d3-a456-426614174000",
        "username": "author123",
        "profile_image_path": "https://example.com/images/author.jpg"
      }
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 10
}
```

---

### 3.3 특정 게시글 조회

**GET** `/posts/{post_id}`

특정 게시글을 조회합니다. 조회 시 조회수가 증가합니다.

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Response (200)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "첫 번째 게시글",
  "content": "이것은 첫 번째 게시글의 내용입니다.",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "views": 11,
  "likes": 5,
  "is_active": true,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "author123",
    "profile_image_path": "https://example.com/images/author.jpg"
  }
}
```

#### Errors

- **404 Not Found**: 게시글을 찾을 수 없음

---

### 3.4 게시글 검색

**GET** `/posts/search`

키워드로 게시글을 검색합니다.

#### Query Parameters

- `keyword` (string): 검색 키워드
- `skip` (int, optional): 건너뛸 게시글 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 게시글 수 (기본값: 10, 최대: 100)

#### Response (200)

```json
{
  "posts": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "검색 키워드가 포함된 게시글",
      "content": "검색 키워드가 포함된 내용입니다.",
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "views": 5,
      "likes": 2,
      "is_active": true,
      "created_at": "2023-10-01T12:00:00Z",
      "updated_at": "2023-10-01T12:00:00Z",
      "author": {
        "id": "456e7890-e89b-12d3-a456-426614174000",
        "username": "author123",
        "profile_image_path": "https://example.com/images/author.jpg"
      }
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 10
}
```

---

### 3.5 게시글 업데이트

**PATCH** `/posts/{post_id}`

게시글을 업데이트합니다. (작성자 또는 관리자만 가능)

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Request Body

```json
{
  "title": "업데이트된 제목",
  "content": "업데이트된 내용입니다."
}
```

#### Response (200)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "업데이트된 제목",
  "content": "업데이트된 내용입니다.",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "views": 11,
  "likes": 5,
  "is_active": true,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T13:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "author123",
    "profile_image_path": "https://example.com/images/author.jpg"
  }
}
```

---

### 3.6 게시글 비활성화

**PATCH** `/posts/{post_id}/deactivate`

게시글을 비활성화합니다. (작성자 또는 관리자만 가능)

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (200)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "비활성화된 게시글",
  "content": "이 게시글은 비활성화되었습니다.",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "views": 11,
  "likes": 5,
  "is_active": false,
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T14:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "author123",
    "profile_image_path": "https://example.com/images/author.jpg"
  }
}
```

---

### 3.7 게시글 삭제

**DELETE** `/posts/{post_id}`

게시글을 삭제합니다. (작성자 또는 관리자만 가능)

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (204)

No content

---

### 3.8 게시글 댓글 목록 조회

**GET** `/posts/{post_id}/comments`

특정 게시글의 댓글 목록을 조회합니다.

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Query Parameters

- `skip` (int, optional): 건너뛸 댓글 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 댓글 수 (기본값: 10, 최대: 100)

#### Response (200)

```json
{
  "comments": [
    {
      "id": "789e1234-e89b-12d3-a456-426614174000",
      "post_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "content": "좋은 게시글이네요!",
      "is_active": true,
      "created_at": "2023-10-01T13:00:00Z",
      "updated_at": "2023-10-01T13:00:00Z",
      "author": {
        "id": "456e7890-e89b-12d3-a456-426614174000",
        "username": "commenter123",
        "profile_image_path": "https://example.com/images/commenter.jpg"
      }
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 10
}
```

---

## 4. 댓글 (Comments)

### 4.1 댓글 생성

**POST** `/comments/`

새로운 댓글을 생성합니다.

#### Headers

```
Authorization: Bearer <token>
```

#### Request Body

```json
{
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "이 게시글 정말 유익하네요!"
}
```

#### Response (201)

```json
{
  "id": "789e1234-e89b-12d3-a456-426614174000",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "content": "이 게시글 정말 유익하네요!",
  "is_active": true,
  "created_at": "2023-10-01T13:00:00Z",
  "updated_at": "2023-10-01T13:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "commenter123",
    "profile_image_path": "https://example.com/images/commenter.jpg"
  }
}
```

---

### 4.2 특정 댓글 조회

**GET** `/comments/{comment_id}`

특정 댓글을 조회합니다.

#### Path Parameters

- `comment_id` (string): 댓글 ID

#### Response (200)

```json
{
  "id": "789e1234-e89b-12d3-a456-426614174000",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "content": "이 게시글 정말 유익하네요!",
  "is_active": true,
  "created_at": "2023-10-01T13:00:00Z",
  "updated_at": "2023-10-01T13:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "commenter123",
    "profile_image_path": "https://example.com/images/commenter.jpg"
  }
}
```

#### Errors

- **404 Not Found**: 댓글을 찾을 수 없음

---

### 4.3 댓글 업데이트

**PATCH** `/comments/{comment_id}`

댓글을 업데이트합니다. (작성자 또는 관리자만 가능)

#### Path Parameters

- `comment_id` (string): 댓글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Request Body

```json
{
  "content": "업데이트된 댓글 내용입니다."
}
```

#### Response (200)

```json
{
  "id": "789e1234-e89b-12d3-a456-426614174000",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "content": "업데이트된 댓글 내용입니다.",
  "is_active": true,
  "created_at": "2023-10-01T13:00:00Z",
  "updated_at": "2023-10-01T14:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "commenter123",
    "profile_image_path": "https://example.com/images/commenter.jpg"
  }
}
```

---

### 4.4 댓글 비활성화

**PATCH** `/comments/{comment_id}/deactivate`

댓글을 비활성화합니다. (작성자 또는 관리자만 가능)

#### Path Parameters

- `comment_id` (string): 댓글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (200)

```json
{
  "id": "789e1234-e89b-12d3-a456-426614174000",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "content": "비활성화된 댓글입니다.",
  "is_active": false,
  "created_at": "2023-10-01T13:00:00Z",
  "updated_at": "2023-10-01T15:00:00Z",
  "author": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "username": "commenter123",
    "profile_image_path": "https://example.com/images/commenter.jpg"
  }
}
```

---

### 4.5 댓글 삭제

**DELETE** `/comments/{comment_id}`

댓글을 삭제합니다. (작성자 또는 관리자만 가능)

#### Path Parameters

- `comment_id` (string): 댓글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (204)

No content

---

## 5. 좋아요 (Likes)

### 5.1 게시글 좋아요 추가

**POST** `/likes/posts/{post_id}`

게시글에 좋아요를 추가합니다.

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (201)

```json
{
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-e89b-12d3-a456-426614174000",
  "created_at": "2023-10-01T15:00:00Z"
}
```

#### Errors

- **409 Conflict**: 이미 좋아요를 누른 게시글
- **404 Not Found**: 게시글을 찾을 수 없음

---

### 5.2 게시글 좋아요 토글

**POST** `/likes/posts/{post_id}/toggle`

게시글 좋아요를 토글합니다. (있으면 삭제, 없으면 생성)

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (200)

```json
{
  "liked": true,
  "message": "좋아요가 추가되었습니다.",
  "like": {
    "post_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "456e7890-e89b-12d3-a456-426614174000",
    "created_at": "2023-10-01T15:00:00Z"
  }
}
```

좋아요 제거 시:

```json
{
  "liked": false,
  "message": "좋아요가 취소되었습니다.",
  "like": null
}
```

---

### 5.3 게시글 좋아요 목록 조회

**GET** `/likes/posts/{post_id}`

특정 게시글의 좋아요 목록을 조회합니다.

#### Path Parameters

- `post_id` (string): 게시글 ID

#### Query Parameters

- `skip` (int, optional): 건너뛸 좋아요 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 좋아요 수 (기본값: 10, 최대: 100)

#### Response (200)

```json
{
  "likes": [
    {
      "post_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "created_at": "2023-10-01T15:00:00Z"
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 10
}
```

---

### 5.4 사용자 좋아요 목록 조회

**GET** `/likes/users/{user_id}`

특정 사용자의 좋아요 목록을 조회합니다.

#### Path Parameters

- `user_id` (string): 사용자 ID

#### Query Parameters

- `skip` (int, optional): 건너뛸 좋아요 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 좋아요 수 (기본값: 10, 최대: 100)

#### Response (200)

```json
{
  "likes": [
    {
      "post_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "created_at": "2023-10-01T15:00:00Z"
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 10
}
```

---

### 5.5 좋아요 삭제

**DELETE** `/likes/posts/{post_id}/users/{user_id}`

특정 게시글의 좋아요를 삭제합니다. (본인 좋아요만 삭제 가능)

#### Path Parameters

- `post_id` (string): 게시글 ID
- `user_id` (string): 사용자 ID

#### Headers

```
Authorization: Bearer <token>
```

#### Response (204)

No content

#### Errors

- **403 Forbidden**: 다른 사용자의 좋아요를 삭제할 권한이 없음
- **404 Not Found**: 좋아요를 찾을 수 없음

---

## 6. 시스템

### 6.1 헬스 체크

**GET** `/health`

애플리케이션 상태를 확인합니다.

#### Response (200)

```json
{
  "status": "ok",
  "database_url": "postgresql://***"
}
```

---

### 6.2 루트

**GET** `/`

API 루트 엔드포인트입니다.

#### Response (200)

```json
{
  "message": "낯가리는 사람들 API"
}
```

---

## 공통 HTTP 상태 코드

- **200 OK**: 요청이 성공적으로 처리됨
- **201 Created**: 리소스가 성공적으로 생성됨
- **204 No Content**: 요청이 성공적으로 처리되었지만 반환할 내용이 없음
- **400 Bad Request**: 잘못된 요청 형식
- **401 Unauthorized**: 인증이 필요하거나 인증 정보가 유효하지 않음
- **403 Forbidden**: 권한이 없음
- **404 Not Found**: 요청한 리소스를 찾을 수 없음
- **409 Conflict**: 리소스 충돌 (중복 생성 등)
- **422 Unprocessable Entity**: 요청 데이터 유효성 검사 실패
- **500 Internal Server Error**: 서버 내부 오류

---

## 예제 사용법

### 1. 사용자 등록 및 로그인

```bash
# 사용자 등록
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'

# 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. 게시글 작성 및 조회

```bash
# 게시글 작성
curl -X POST "http://localhost:8000/api/v1/posts/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "첫 번째 게시글",
    "content": "안녕하세요, 첫 번째 게시글입니다."
  }'

# 게시글 목록 조회
curl -X GET "http://localhost:8000/api/v1/posts/"
```

### 3. 댓글 작성 및 좋아요

```bash
# 댓글 작성
curl -X POST "http://localhost:8000/api/v1/comments/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "<post-id>",
    "content": "좋은 게시글이네요!"
  }'

# 좋아요 토글
curl -X POST "http://localhost:8000/api/v1/likes/posts/<post-id>/toggle" \
  -H "Authorization: Bearer <your-token>"
```
