# P01: 프로젝트 개요 (Project Overview)

## 📋 프로젝트 정보

**프로젝트명**: 사주 챗봇 (Korean Fortune Telling Chatbot)
**버전**: 1.0.0
**언어**: Python 3.8+
**프레임워크**: FastAPI, LangChain, LangGraph
**개발 기간**: 2024년

## 🎯 프로젝트 목적

한국 전통 사주 명리학을 기반으로 한 AI 챗봇 시스템을 구축하여 사용자에게 개인화된 운세 상담 서비스를 제공합니다.

### 핵심 목표
- **전통 명리학의 디지털화**: 천간지지, 오행, 십성 등 전통 사주 이론의 체계적 구현
- **자연스러운 대화**: LangGraph를 활용한 상태 기반 대화 흐름 구현
- **정확한 계산**: 음력-양력 변환, 절기 계산 등 정밀한 사주 계산 시스템
- **지식 기반 추론**: Vector DB를 활용한 사주 지식 검색 및 해석
- **확장 가능한 아키텍처**: 마이크로서비스 패턴을 적용한 모듈형 설계

## 🏗️ 시스템 아키텍처 개요

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LangGraph     │    │   Core Modules  │
│   Web Server    │◄──►│   Workflow      │◄──►│   Calculator    │
│                 │    │   Engine        │    │   Analyzer      │
└─────────────────┘    └─────────────────┘    │   Interpreter   │
         │                       │             └─────────────────┘
         ▼                       ▼                       │
┌─────────────────┐    ┌─────────────────┐              ▼
│   Session       │    │   Vector DB     │    ┌─────────────────┐
│   Management    │    │   (ChromaDB)    │    │   Knowledge     │
│   (MySQL)       │    │                 │    │   Base          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 핵심 기술 스택

### Backend Framework
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Uvicorn**: ASGI 서버

### AI & ML
- **LangChain**: LLM 체인 및 도구 관리
- **LangGraph**: 상태 기반 대화 워크플로우
- **OpenAI GPT-4**: 자연어 처리 및 생성
- **ChromaDB**: 벡터 데이터베이스
- **HuggingFace Transformers**: 한국어 임베딩 (`jhgan/ko-sroberta-multitask`)

### Database & Storage
- **MySQL**: 세션 및 사용자 데이터 저장
- **ChromaDB**: 사주 지식 벡터 저장소

### Development Tools
- **pytest**: 테스트 프레임워크
- **python-dotenv**: 환경변수 관리
- **pydantic**: 데이터 검증

## 📁 프로젝트 구조

```
saju_chatbot_v1/
├── app.py                 # FastAPI 메인 애플리케이션
├── main.py               # 콘솔 인터페이스
├── test_saju.py          # 시스템 통합 테스트
│
├── chatbot/              # 챗봇 워크플로우
│   ├── graph.py          # LangGraph 상태 그래프
│   ├── state.py          # 대화 상태 관리
│   └── tools.py          # 사주 계산 도구들
│
├── core/                 # 핵심 사주 계산 모듈
│   ├── saju_calculator.py    # 사주 계산 엔진
│   ├── saju_analyzer.py      # 오행/십성 분석
│   └── saju_interpreter.py   # 사주 해석
│
├── database/             # 데이터베이스 관리
│   ├── mysql_manager.py      # MySQL 세션 관리
│   └── chroma_manager.py     # Vector DB 관리
│
├── data/                 # 사주 지식 데이터
│   ├── saju_terms.json       # 전통 용어 사전
│   └── saju_rules.json       # 해석 규칙
│
├── tests/                # 정형 테스트 스위트
├── playground/           # 실험/개발용 테스트
└── docs/                # 프로젝트 문서
```

## 🌟 주요 기능

### 1. 사주 계산 (Saju Calculation)
- 생년월일시를 천간지지로 변환
- 음력-양력 변환 및 절기 계산
- 대운, 세운 계산

### 2. 오행 분석 (Five Elements Analysis)
- 오행(목화토금수) 균형 분석
- 용신, 희신 추출
- 계절별 강약 판단

### 3. 십성 분석 (Ten Gods Analysis)
- 비견, 겁재, 식신, 상관, 편재, 정재, 편관, 정관, 편인, 정인 분석
- 성격, 재물운, 관운 해석

### 4. 신살 분석 (Gods and Demons)
- 길신, 흉신 추출
- 특수 운세 요소 분석

### 5. 대화형 상담
- 자연어 질문 이해
- 맥락 기반 답변 생성
- 세션 기반 대화 지속

## 🎯 타겟 사용자

### Primary Users
- **개인 사용자**: 자신의 운세를 알고 싶어하는 일반인
- **사주 학습자**: 명리학을 공부하는 입문자/중급자

### Secondary Users
- **사주 전문가**: 상담 보조 도구로 활용
- **개발자**: 사주 시스템을 이해하고 확장하려는 개발자

## 📈 성능 및 확장성

### 성능 목표
- **응답 시간**: 평균 2초 이내
- **동시 사용자**: 100명 이상
- **정확도**: 전통 사주 계산 대비 99% 이상

### 확장성 고려사항
- 모듈형 아키텍처로 기능별 독립 확장 가능
- Vector DB를 통한 지식 베이스 지속적 확장
- RESTful API 설계로 다양한 클라이언트 지원

## 🔒 보안 및 개인정보

### 데이터 보호
- 생년월일시 등 민감 정보 암호화 저장
- 세션 기반 임시 데이터 관리
- GDPR 및 개인정보보호법 준수

### API 보안
- 입력 데이터 검증 및 새니타이제이션
- Rate limiting으로 남용 방지
- 에러 정보 노출 최소화

## 🚀 향후 로드맵

### Phase 2 (향후 6개월)
- [ ] 웹 프론트엔드 개발
- [ ] 모바일 앱 지원
- [ ] 음성 인터페이스 추가

### Phase 3 (향후 1년)
- [ ] 다중 언어 지원
- [ ] 개인화 추천 시스템
- [ ] 소셜 기능 추가

### Phase 4 (장기)
- [ ] 머신러닝 기반 예측 모델
- [ ] 블록체인 기반 신뢰성 보장
- [ ] B2B 서비스 확장

---

**문서 작성자**: Claude Code (Anthropic)
**최종 업데이트**: 2024년
**다음 문서**: [P02: 개발환경 설정 가이드](p02_setup_guide.md)