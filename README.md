# 낯가리는 사람들... [BE FastAPI 리팩토링]

### 프로젝트 소개

낯가리는 수많은 내향인들을 위한 커뮤니티 '낯가리는 사람들'의 백엔드를 FastAPI로 리팩토링한 프로젝트입니다.

기존 Node.js 프로젝트의 유지보수성 및 확장성 개선, 타입 시스템을 통한 안정성 확보, 최신 기술 스택 경험 등을 위해 FastAPI로 리팩토링을 결정했습니다

> **개발 기간** : _2025.6 ~2025.7_ <br/>

> **개인 프로젝트**<br/>

### 개발 스택

<div style="display:flex;gap:10px;flex-wrap:wrap;">
    <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white">
</div>

<!-- ### 시연 영상

[![Video](https://github.com/user-attachments/assets/dde71ff1-8b25-4f25-a045-ad1a6c8f7740)](https://drive.google.com/file/d/1A8YiR0NgGE1wewpjMH1udUsXipLmZTcJ/view?usp=sharing) -->

### 프로젝트 구조

```
project/
│  .env
│  .env.local
│  .gitignore
│  .pre-commit-config.yaml
│  dev.db
│  poetry.lock
│  pyproject.toml
│  pyrefly.toml
│  README.md
├─src
│  │  main.py
│  │
│  ├─auth
│  │  │  crud.py
│  │  │  dependencies.py
│  │  │  exceptions.py
│  │  │  models.py
│  │  │  models.pyi
│  │  │  router.py
│  │  │  schemas.py
│  │  │  service.py
│  │  │  __init__.py
│  ├─comments
│  │  │  crud.py
│  │  │  dependencies.py
│  │  │  models.py
│  │  │  models.pyi
│  │  │  router.py
│  │  │  schemas.py
│  │  │  service.py
│  │  │  __init__.py
│  ├─common
│  │  │  crud.py
│  │  │  schemas.py
│  ├─core
│  │  │  config.py
│  │  │  security.py
│  ├─db
│  │  │  base.py
│  │  │  session.py
│  │  │  __init__.py
│  ├─likes
│  │  │  models.py
│  │  │  models.pyi
│  │  │  schemas.py
│  │  │  __init__.py
│  ├─posts
│  │  │  crud.py
│  │  │  dependencies.py
│  │  │  models.py
│  │  │  models.pyi
│  │  │  README.md
│  │  │  router.py
│  │  │  schemas.py
│  │  │  service.py
│  │  │  __init__.py
│  ├─scripts
│  │      init_db.py
│  ├─users
│  │  │  crud.py
│  │  │  dependencies.py
│  │  │  models.py
│  │  │  models.pyi
│  │  │  README.md
│  │  │  router.py
│  │  │  schemas.py
│  │  │  service.py
│  │  │  __init__.py
└─tests
    │  conftest.py
    │  README.md
    │  test_main.py
    │  __init__.py
    ├─auth
    │  │  test_auth_crud.py
    │  │  test_auth_service.py
    │  │  __init__.py
    ├─core
    │  │  test_security.py
    ├─posts
    │  │  test_posts_crud.py
    │  │  test_posts_service.py
    │  │  __init__.py
    ├─users
    │  │  test_users_crud.py
    │  │  test_users_dependencies.py
    │  │  test_users_service.py
    │  │  __init__.py
```

### 프로젝트 세부 사항

본 프로젝트는 기능별로 분리된 모듈식 구조를 채택하여 유지보수성과 확장성을 높였습니다. 각 기능(auth, users, posts, comments)은 자체적인 router, service, crud 레이어를 가지며 아키텍처는 각자의 역할과 책임이 명확하게 분리할 수 있도록 구성되어 있습니다.

- API Endpoints (`router.py`): HTTP 요청을 수신하고 응답을 반환하는 API 인터페이스 계층입니다.
- Business Logic (`service.py`): 실제 비즈니스 로직을 처리하는 서비스 계층입니다.
- Data Access (`crud.py`): 데이터베이스와의 상호작용(CRUD)을 담당하는 데이터 접근 계층입니다.
- Data Models (`models.py`, `schemas.py`): SQLAlchemy 모델과 Pydantic 스키마를 통해 데이터를 정의하고 검증합니다.

**주요 특징**

1. FastAPI 기반의 고성능 비동기 API
   - Python의 ASGI 표준을 기반으로 한 FastAPI를 사용하여 async/await 문법으로 논블로킹(Non-blocking) I/O를 처리합니다. FastAPI를 채택한 가장 큰 이유이기도 합니다. 이를 통해 기존 타 언어나 파이썬의 동기 방식 프레임워크 대비 월등히 높은 성능과 처리량을 자랑합니다.

2. Pydantic을 통한 강력한 데이터 검증
   - 버그를 줄이고 API의 안정성을 크게 향상시키기 위해 Python 타입 힌트를 활용하는 Pydantic을 통해 API 요청 및 응답 데이터의 유효성을 런타임에 자동으로 검증합니다. 
   - FastAPI가 자동으로 생성해주는 Swagger UI 및 ReDoc API 문서를 통해 별도의 문서 작업 없이 API 명세를 확인하고 테스트했습니다.

3. 체계적인 프로젝트 구조와 클린 아키텍처 지향
   - 기능별 모듈화와 관심사 분리(Separation of Concerns) 원칙에 따라 프로젝트 구조를 설계하여, 새로운 기능을 추가하거나 기존 코드를 수정하기 용이합니다.

4. SQLAlchemy를 사용한 ORM
    - FastAPI에서 사실상 표준인 Python ORM인 SQLAlchemy를 사용하여 데이터베이스 작업을 객체 지향적으로 처리하고, 이를 통해 특정 데이터베이스에 대한 종속성을 줄이고 코드의 가독성을 높입니다. 개발 단계에서는 SQLite를 사용했습니다.

5. JWT 기반의 안전한 인증 시스템
   - JWT(JSON Web Token)를 사용한 토큰 기반 인증을 구현하여 상태 비저장(Stateless)이면서도 안전한 API를 제공합니다.

6. 코드 품질 및 자동화된 테스트
   - pre-commit 훅과 Ruff 린터를 사용하여 일관된 코드 스타일을 유지하고 잠재적인 오류를 사전에 방지합니다.
   - Pytest를 사용한 단위 테스트 및 통합 테스트 코드를 작성하여 코드의 신뢰성과 안정성을 보장합니다.
