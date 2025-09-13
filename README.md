# 낯가리는 사람들... [BE FastAPI 리팩토링]

## 프로젝트 소개

낯가리는 수많은 내향인들을 위한 커뮤니티 '낯가리는 사람들'의 백엔드 시스템을 기존 Node.js에서 Python FastAPI로 리팩토링한 아키텍처 개선 프로젝트입니다.

본 리팩토링 프로젝트의 주요 목표는 다음과 같습니다.

1. 성능 및 확장성 확보: FastAPI의 비동기 I/O 모델을 도입해 병목 현상을 최소화하고, 대규모 트래픽에 대응할 수 있는 확장 가능한 아키텍처를 구축.

2. 코드 안정성 강화: Python의 엄격한 타입 힌트와 Pydantic의 데이터 검증을 활용해, 런타임 오류를 사전에 방지하고, 코드의 예측 가능성과 신뢰성을 높임.

3. 유지보수 효율 증대: 관심사 분리 원칙에 따라 API, 비즈니스 로직, 데이터 접근 계층으로 코드를 분리했습니다. 또한 의존성 주입(DI)을 통해 컴포넌트 간의 결합도를 낮추고 기능 추가 및 변경과 테스트하기에 용이한 아키텍처로 변경.

4. 테스트 커버리지 확대: 유닛 테스트를 프로젝트 전반에 도입함으로서 높은 테스트 커버리지를 달성. 코드 변경에 대한 안정성을 증대하며 잠재적인 디버깅 시간을 크게 개선.

> **개발 기간** : _2025.6 ~2025.7_ <br/>

> **개인 프로젝트**<br/>

## 개발 스택

<div style="display:flex;gap:10px;flex-wrap:wrap;">
    <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white">
</div>

## 시연 영상

[![Video](https://github.com/user-attachments/assets/dde71ff1-8b25-4f25-a045-ad1a6c8f7740)](https://drive.google.com/file/d/1A8YiR0NgGE1wewpjMH1udUsXipLmZTcJ/view?usp=sharing)

## API 명세

자세한 API 명세는 아래 링크에서 확인하실 수 있습니다.

[API 명세서 바로가기](./api.md)

## 프로젝트 구조 & 세부 사항

<details>
    <summary>프로젝트 구조 보기</summary>

```
project/
│  .env.example
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
│  │  │  crud.py
│  │  │  dependencies.py
│  │  │  models.py
│  │  │  models.pyi
│  │  │  router.py
│  │  │  schemas.py
│  │  │  service.py
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

</details>

### 프로젝트 세부 사항

본 프로젝트는 기능별로 분리된 모듈식 구조를 채택하여 유지보수성과 확장성을 높였습니다. 각 기능(auth, users, posts, comments, likes)은 자체적인 router, service, crud 레이어를 가지며 아키텍처는 각자의 역할과 책임이 명확하게 분리할 수 있도록 구성되어 있습니다.

- API Endpoints (`router.py`): HTTP 요청을 수신하고 응답을 반환하는 API 인터페이스 계층입니다.
- Business Logic (`service.py`): 실제 비즈니스 로직을 처리하는 서비스 계층입니다.
- Data Access (`crud.py`): 데이터베이스와의 상호작용(CRUD)을 담당하는 데이터 접근 계층입니다.
- Data Models (`models.py`, `schemas.py`): SQLAlchemy 모델과 Pydantic 스키마를 통해 데이터를 정의하고 검증합니다.
- 의존성 (`dependencies.py`): 공통적으로 사용되는 의존성을 정리하고 재사용 가능한 로직을 분리해 코드의 중복을 줄이며 테스트를 용이하게 합니다.
