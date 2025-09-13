# 낯가리는 사람들... [BE FastAPI 리팩토링]

## 프로젝트 소개

낯가리는 수많은 내향인들을 위한 커뮤니티 '낯가리는 사람들'의 백엔드 시스템을 기존 Node.js에서 Python FastAPI로 리팩토링한 아키텍처 개선 프로젝트입니다.

본 리팩토링 프로젝트의 주요 목표는 다음과 같습니다.

1. 성능 및 확장성 확보: FastAPI의 비동기 I/O 모델을 도입해 병목 현상을 최소화하고, 대규모 트래픽에 대응할 수 있는 확장 가능한 아키텍처를 구축.

2. 코드 안정성 강화: Python의 엄격한 타입 힌트와 Pydantic의 데이터 검증을 활용해, 런타임 오류를 사전에 방지하고, 코드의 예측 가능성과 신뢰성을 높임.

3. 유지보수 효율 증대: 관심사 분리 원칙에 따라 API, 비즈니스 로직, 데이터 접근 계층으로 코드를 분리했습니다. 또한 의존성 주입(DI)을 통해 컴포넌트 간의 결합도를 낮추고 기능 추가 및 변경과 테스트하기에 용이한 아키텍처로 변경.

4. 테스트 커버리지 확대: 유닛 테스트를 프로젝트 전반에 도입함으로서 높은 테스트 커버리지를 달성. 코드 변경에 대한 안정성을 증대하며 잠재적인 디버깅 시간을 크게 개선.

> **개발 기간** : _2025.6 ~2025.9_ <br/>

> **개인 프로젝트**<br/>

## 리팩토링 주요 성과

### 주요 기술 선택과 해결 방안

- **Node.js -> FastAPI**
  - **타입 안정성**: Python 타입 힌트와 Pydantic 데이터 검증
  - **비동기 처리**: ASGI 기반 멀티 프로세싱 지원
  - **개발 생산성**: 별도 문서화 도구가 필요 없으며, 높은 생산성과 가독성을 제공하는 Python
- **주요 설계**
  - Soft Delete로 사용자 데이터 완전 삭제 방지
  - JTI 블락리스트와 토큰 버전 관리로 인증 구현

### 성능 개선 결과

_로컬 환경 기준_

- **평균 응답시간 26-101ms**
- **처리량 111-130 RPS (동시 요청 5-20개 처리 시 선형적 확장성 유지)**
- **동시 요청 20배 증가 시에도 100% 성공률 유지**
- **메모리 사용량 누수 없음, 31.3MB 고정**

### 코드 품질 향상

- **테스트 커버리지 82% (CRUD 계층 100%)**
- **Pydantic 검증과 타입 힌트 도입으로 런타임 오류 감소**
- **의존성 주입으로 테스트 용이성 및 모듈 간 결합도를 감소**
- **계층 분리를 통한 유지보수성 향상**

### 개발 경험 향상

- 자동 문서화: OpenAPI 기반 상호작용 가능한 API 문서 제공
- 테스트 작성: 테스트 코드 작성으로 에러 처리 효율과 검증 시간 단축
- 개발 속도: 타입 힌트 기반 + IDE 자동 완성으로 효율성 증대
- 디버깅 효율성: 에러 메시지와 스택 트레이스 확인

**-> 사용자 경험을 개선하고, 개발 효율성을 증대시킬 수 있음을 확인**

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

### 벤치마크 환경

- **테스트 도구**: Python 기반 동시성 테스트 스크립트
- **측정 지표**: 응답시간, 처리량, 메모리 사용량, 성공률
- **시나리오**: 실제 API 엔드포인트 기반 (게시글 조회)
- 동일 하드웨어 환경에서 일관된 조건으로 측정
