# 사주 챗봇 API 테스트 가이드

## 개요

이 문서는 사주 챗봇 FastAPI 애플리케이션의 테스트 구조와 실행 방법을 설명합니다.

## 테스트 구조

```
tests/
├── __init__.py              # 테스트 패키지 초기화
├── conftest.py             # pytest fixtures 및 설정
├── test_api.py             # API 엔드포인트 테스트
├── test_models.py          # Pydantic 모델 테스트
└── test_performance.py     # 성능 및 부하 테스트
```

## 테스트 환경 설정

### 1. 의존성 설치

```bash
pip install pytest pytest-asyncio httpx pytest-mock pytest-cov
```

### 2. 환경 변수 설정

테스트 실행 전 `.env` 파일이 올바르게 설정되어 있는지 확인하세요:

```env
OPENAI_API_KEY="your-openai-api-key"
OPENAI_MODEL="gpt-4o-mini"
OPENAI_TEMPERATURE="0.3"
OPENAI_MAX_TOKENS="2000"
MYSQL_HOST="localhost"
MYSQL_USER="your-username"
MYSQL_PASSWORD="your-password"
MYSQL_DB="saju_chatbot_db"
```

## 테스트 실행 방법

### 1. 전체 테스트 실행

```bash
python -m pytest tests/ -v
```

### 2. 특정 테스트 파일 실행

```bash
# API 테스트만 실행
python -m pytest tests/test_api.py -v

# 모델 테스트만 실행
python -m pytest tests/test_models.py -v

# 성능 테스트만 실행 (빠른 테스트)
python -m pytest tests/test_performance.py -v -m "not slow"
```

### 3. 커버리지 포함 테스트

```bash
python -m pytest tests/ --cov=app --cov=chatbot --cov=core --cov=database --cov-report=html
```

### 4. 테스트 실행 스크립트 사용

```bash
# 모든 테스트
python run_tests.py --all

# API 테스트만
python run_tests.py --api

# 성능 테스트
python run_tests.py --performance

# 커버리지 포함
python run_tests.py --coverage
```

## 테스트 클래스별 상세 설명

### TestChatAPI (test_api.py)

**목적**: 채팅 API의 기본 동작 테스트

**주요 테스트 케이스**:
- `test_chat_basic_request`: 기본 채팅 요청/응답 테스트
- `test_chat_with_history`: 대화 기록이 있는 요청 테스트
- `test_chat_without_session_id`: 새 세션 생성 테스트
- `test_chat_with_existing_session_data`: 기존 세션 데이터 로드 테스트
- `test_chat_tool_message_response`: 도구 메시지 응답 처리 테스트
- `test_chat_error_handling`: 오류 상황 처리 테스트
- `test_chat_no_response_message`: 응답 없는 상황 테스트
- `test_chat_invalid_request_format`: 잘못된 요청 형식 테스트

### TestAPIValidation (test_api.py)

**목적**: API 입력 검증 로직 테스트

**주요 테스트 케이스**:
- `test_empty_message`: 빈 메시지 처리 테스트
- `test_long_message`: 긴 메시지 처리 테스트
- `test_special_characters_in_message`: 특수문자/이모지 처리 테스트

### TestAPIIntegration (test_api.py)

**목적**: 전체 API 플로우 통합 테스트

**주요 테스트 케이스**:
- `test_full_conversation_flow`: 다단계 대화 플로우 테스트

### TestChatRequest (test_models.py)

**목적**: Pydantic 모델 검증 테스트

**주요 테스트 케이스**:
- `test_valid_chat_request`: 유효한 요청 모델 생성 테스트
- `test_chat_request_without_session_id`: 선택적 필드 테스트
- `test_chat_request_missing_user_id`: 필수 필드 누락 검증 테스트
- `test_chat_request_with_complex_history`: 복잡한 대화 기록 처리 테스트
- `test_chat_request_unicode_message`: 유니코드 문자 처리 테스트

### TestAPIPerformance (test_performance.py)

**목적**: API 성능 및 확장성 테스트

**주요 테스트 케이스**:
- `test_single_request_response_time`: 단일 요청 응답 시간 측정
- `test_concurrent_requests`: 동시 요청 처리 성능 테스트
- `test_large_payload_handling`: 대용량 데이터 처리 성능 테스트
- `test_memory_usage_with_long_conversation`: 긴 대화에서 메모리 사용량 테스트

### TestAPIStress (test_performance.py)

**목적**: 스트레스 테스트 및 오류 복구

**주요 테스트 케이스**:
- `test_sustained_load`: 지속적인 부하 테스트 (30초간)
- `test_error_recovery`: 시스템 오류 복구 테스트

## Mock 객체 활용

테스트에서는 외부 의존성을 최소화하기 위해 다음 컴포넌트들을 Mock으로 처리합니다:

### conftest.py의 주요 Fixtures

```python
@pytest.fixture
def mock_mysql_manager():
    """MySQL Manager mock - 데이터베이스 연결 없이 테스트"""

@pytest.fixture
def mock_saju_graph():
    """Saju Graph mock - LangGraph 실행 없이 테스트"""

@pytest.fixture
def mock_chroma_manager():
    """ChromaDB Manager mock - 벡터DB 없이 테스트"""

@pytest.fixture
async def client():
    """AsyncClient fixture - FastAPI 테스트 클라이언트"""
```

## 테스트 마커

pytest.ini에서 정의된 마커들:

- `@pytest.mark.slow`: 느린 테스트 (5초 이상)
- `@pytest.mark.integration`: 통합 테스트
- `@pytest.mark.unit`: 단위 테스트
- `@pytest.mark.api`: API 테스트
- `@pytest.mark.performance`: 성능 테스트

### 마커 사용 예시

```bash
# 느린 테스트 제외하고 실행
python -m pytest -m "not slow"

# 성능 테스트만 실행
python -m pytest -m "performance"

# API 테스트만 실행
python -m pytest -m "api"
```

## CI/CD 통합

### GitHub Actions 예시

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/ --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 테스트 작성 가이드라인

### 1. 테스트 네이밍

```python
def test_should_return_success_when_valid_request():
    """테스트 함수명은 명확하고 구체적으로"""
```

### 2. AAA 패턴 (Arrange, Act, Assert)

```python
def test_example():
    # Arrange (준비)
    request_data = {"user_id": "test", "message": "hello"}

    # Act (실행)
    response = await client.post("/chat/", json=request_data)

    # Assert (검증)
    assert response.status_code == 200
    assert "response" in response.json()
```

### 3. 독립성 유지

- 각 테스트는 독립적으로 실행 가능해야 함
- 테스트 순서에 의존하지 않아야 함
- 외부 상태에 의존하지 않아야 함

### 4. 의미있는 테스트 데이터

```python
@pytest.fixture
def sample_birth_info():
    """의미있는 테스트 데이터 사용"""
    return {
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": 14
    }
```

## 트러블슈팅

### 자주 발생하는 문제들

1. **ImportError**: 모듈을 찾을 수 없는 경우
   - `sys.path`에 프로젝트 루트 추가 확인
   - `__init__.py` 파일 존재 확인

2. **AsyncIO 관련 오류**
   - `pytest-asyncio` 설치 확인
   - `pytest.ini`에서 `asyncio_mode = auto` 설정 확인

3. **Mock 관련 오류**
   - `pytest-mock` 설치 확인
   - Mock 객체의 메서드/속성 올바른 설정 확인

4. **환경변수 문제**
   - `.env` 파일 위치 및 내용 확인
   - `python-dotenv` 설치 확인

## 성능 기준

테스트에서 사용하는 성능 기준:

- **단일 요청 응답 시간**: 5초 이내
- **동시 요청 처리**: 10개 요청을 10초 이내 처리
- **대용량 데이터**: 10MB 이하 페이로드를 10초 이내 처리
- **지속 부하**: 30초간 95% 이상 성공률 유지
- **메모리 사용**: 50회 연속 대화 후에도 정상 동작

이러한 기준은 실제 운영 환경에 맞게 조정할 수 있습니다.