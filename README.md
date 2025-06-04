# 낯가리는 사람들... [BE FastAPI 리팩토링]

## 1. 프로젝트 개요

### 프로젝트 소개

낯가리는 수많은 내향인들을 위한 커뮤니티 '낯가리는 사람들'의 백엔드를 FastAPI로 리팩토링한 프로젝트입니다.

기존 Node.js 프로젝트의 유지보수성 및 확장성 개선, 타입 시스템을 통한 안정성 확보, 최신 기술 스택 경험 등을 위해 FastAPI로 리팩토링을 결정했습니다

> **개발 기간** : _2025.6 ~_ <br/>

> **개인 프로젝트**<br/>

> **URL**: _추가 예정_

### 개발 스택

<div style="display:flex;gap:10px;flex-wrap:wrap;">
    <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white">
</div>

<!-- ### 시연 영상

[![Video](https://github.com/user-attachments/assets/dde71ff1-8b25-4f25-a045-ad1a6c8f7740)](https://drive.google.com/file/d/1A8YiR0NgGE1wewpjMH1udUsXipLmZTcJ/view?usp=sharing) -->

### 예상 프로젝트 구조

```
project/
├── src/
│ ├── main.py # FastAPI 앱 초기화, 전역 구성
│ ├── core/
│ │ └── config.py # 애플리케이션 설정 (예: Pydantic BaseSettings)
│ ├── db/
│ │ ├── session.py # 데이터베이스 세션 관리 (예: get_db 종속성)
│ │ └── base.py # SQLAlchemy Base, 공통 모델 믹스인
│ ├── users/ # 'users'에 대한 예제 도메인 모듈
│ │ ├── init.py
│ │ ├── router.py # 사용자에 대한 API 엔드포인트 (APIRouter)
│ │ ├── schemas.py # 사용자 요청/응답에 대한 Pydantic 스키마
│ │ ├── models.py # 사용자에 대한 SQLAlchemy 모델
│ │ ├── service.py # 사용자 작업에 대한 비즈니스 로직
│ │ ├── crud.py # (또는 repository.py) 사용자에 대한 데이터 액세스 작업
│ │ └── dependencies.py # 사용자별 종속성
│ ├── items/ # 'items'에 대한 또 다른 예제 도메인 모듈
│ │ └──... # users/와 유사한 구조
│ └── common/ # 공유 유틸리티, Pydantic 모델 등
│   └── schemas.py
├── tests/
│ ├── conftest.py # Pytest 픽스처
│ ├── core/
│ │ └── test_config.py
│ ├── users/
│ │ └── test_user_router.py
│ └──...
├──.env # 환경 변수 (커밋되지 않음)
├──.gitignore
├── pyproject.toml # 프로젝트 메타데이터, 종속성, 도구 구성
└── README.md
```
