# P04: API 레퍼런스 (API Reference)

## 🌐 API 개요

사주 챗봇 시스템은 RESTful API 설계 원칙을 따르며, FastAPI 프레임워크를 기반으로 구현되었습니다. 모든 API는 JSON 형식으로 데이터를 주고받으며, OpenAPI 3.0 스펙을 준수합니다.

### 기본 정보
- **Base URL**: `http://localhost:8000` (개발환경)
- **Content-Type**: `application/json`
- **인코딩**: UTF-8
- **API 문서**: `/docs` (Swagger UI), `/redoc` (ReDoc)

## 📋 엔드포인트 목록

| 메서드 | 엔드포인트 | 설명 | 인증 필요 |
|--------|------------|------|-----------|
| POST | `/chat/` | 챗봇과 대화 | ❌ |
| GET | `/health` | 서버 상태 확인 | ❌ |
| GET | `/docs` | API 문서 (Swagger) | ❌ |
| GET | `/redoc` | API 문서 (ReDoc) | ❌ |

## 🤖 채팅 API

### POST /chat/

사주 챗봇과 대화하는 메인 엔드포인트입니다.

#### 요청 (Request)

```http
POST /chat/
Content-Type: application/json

{
    "user_id": "string",
    "session_id": "string | null",
    "message": "string",
    "history": [
        {
            "role": "user | assistant | tool",
            "content": "string",
            "tool_calls": "array | null",
            "tool_call_id": "string | null"
        }
    ]
}
```

#### 요청 스키마

```typescript
interface ChatRequest {
    user_id: string;           // 사용자 고유 식별자
    session_id?: string;       // 세션 ID (없으면 자동 생성)
    message: string;           // 사용자 메시지
    history?: Message[];       // 이전 대화 기록 (선택사항)
}

interface Message {
    role: "user" | "assistant" | "tool";
    content: string;
    tool_calls?: ToolCall[];   // assistant 메시지에만 존재
    tool_call_id?: string;     // tool 메시지에만 존재
}

interface ToolCall {
    id: string;
    type: "function";
    function: {
        name: string;
        arguments: string;     // JSON string
    };
}
```

#### 응답 (Response)

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "session_id": "string",
    "response": "string",
    "full_history": [
        {
            "role": "user | assistant | tool",
            "content": "string",
            "tool_calls": "array | null",
            "tool_call_id": "string | null"
        }
    ]
}
```

#### 응답 스키마

```typescript
interface ChatResponse {
    session_id: string;        // 세션 ID
    response: string;          // 챗봇 응답 메시지
    full_history: Message[];   // 전체 대화 기록
}
```

## 📝 사용 예시

### 1. 첫 대화 시작

```bash
curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "message": "안녕하세요, 사주를 봐주세요",
       "history": []
     }'
```

**응답 예시:**
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "response": "안녕하세요! 사주를 봐드리겠습니다. 먼저 생년월일시를 알려주세요. 양력 기준으로 년, 월, 일, 시간을 정확히 알려주시면 됩니다.",
    "full_history": [
        {
            "role": "user",
            "content": "안녕하세요, 사주를 봐주세요"
        },
        {
            "role": "assistant",
            "content": "안녕하세요! 사주를 봐드리겠습니다. 먼저 생년월일시를 알려주세요. 양력 기준으로 년, 월, 일, 시간을 정확히 알려주시면 됩니다."
        }
    ]
}
```

### 2. 생년월일시 제공

```bash
curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "session_id": "550e8400-e29b-41d4-a716-446655440000",
       "message": "1990년 5월 15일 오후 2시 30분에 태어났습니다",
       "history": [
         {
           "role": "user",
           "content": "안녕하세요, 사주를 봐주세요"
         },
         {
           "role": "assistant",
           "content": "안녕하세요! 사주를 봐드리겠습니다. 먼저 생년월일시를 알려주세요."
         }
       ]
     }'
```

**응답 예시:**
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "response": "1990년 5월 15일 오후 2시 30분생 사주를 계산해드렸습니다.\n\n년주: 庚午(경오)\n월주: 辛巳(신사)\n일주: 甲子(갑자)\n시주: 辛未(신미)\n\n일간 甲木으로 봄에 태어나 목기운이 왕성합니다. 성격이 곧고 정직하며 리더십이 있으신 분입니다...",
    "full_history": [
        {
            "role": "user",
            "content": "안녕하세요, 사주를 봐주세요"
        },
        {
            "role": "assistant",
            "content": "안녕하세요! 사주를 봐드리겠습니다. 먼저 생년월일시를 알려주세요."
        },
        {
            "role": "user",
            "content": "1990년 5월 15일 오후 2시 30분에 태어났습니다"
        },
        {
            "role": "assistant",
            "content": "1990년 5월 15일 오후 2시 30분생 사주를 계산해드렸습니다...",
            "tool_calls": [
                {
                    "id": "call_abc123",
                    "type": "function",
                    "function": {
                        "name": "calculate_saju",
                        "arguments": "{\"year\": 1990, \"month\": 5, \"day\": 15, \"hour\": 14, \"minute\": 30}"
                    }
                }
            ]
        },
        {
            "role": "tool",
            "content": "{\"year_ganji\": \"庚午\", \"month_ganji\": \"辛巳\", \"day_ganji\": \"甲子\", \"time_ganji\": \"辛未\"}",
            "tool_call_id": "call_abc123"
        }
    ]
}
```

### 3. 추가 질문

```bash
curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "session_id": "550e8400-e29b-41d4-a716-446655440000",
       "message": "올해 재물운은 어떤가요?",
       "history": [...]
     }'
```

## 🔧 도구 호출 (Tool Calls)

챗봇은 다음과 같은 도구들을 사용하여 사주 관련 작업을 수행합니다:

### 1. calculate_saju
사용자의 생년월일시를 바탕으로 사주를 계산합니다.

```json
{
    "name": "calculate_saju",
    "arguments": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "is_lunar": false,
        "is_leap_month": false
    }
}
```

### 2. analyze_saju
계산된 사주를 분석하여 오행, 십성 등을 추출합니다.

```json
{
    "name": "analyze_saju",
    "arguments": {
        "saju_data": {
            "year_ganji": "庚午",
            "month_ganji": "辛巳",
            "day_ganji": "甲子",
            "time_ganji": "辛未"
        }
    }
}
```

### 3. search_knowledge
사주 관련 지식을 벡터 데이터베이스에서 검색합니다.

```json
{
    "name": "search_knowledge",
    "arguments": {
        "query": "甲木 성격 특성",
        "limit": 3
    }
}
```

## ❌ 에러 응답

### 일반적인 에러 형식

```json
{
    "detail": "error message"
}
```

### 주요 에러 코드

| 상태 코드 | 설명 | 예시 |
|-----------|------|------|
| 400 | Bad Request | 잘못된 요청 형식 |
| 422 | Validation Error | 필수 필드 누락 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 에러 예시

#### 400 Bad Request
```json
{
    "detail": "Invalid message format"
}
```

#### 422 Validation Error
```json
{
    "detail": [
        {
            "loc": ["body", "user_id"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Internal Server Error: Database connection failed"
}
```

## 🔒 보안 고려사항

### 입력 검증
- 모든 사용자 입력에 대해 길이 제한 및 형식 검증
- HTML/JavaScript 인젝션 방지를 위한 sanitization
- SQL 인젝션 방지를 위한 매개변수화된 쿼리 사용

### 개인정보 보호
- 생년월일시는 암호화하여 데이터베이스에 저장
- 세션 데이터는 일정 시간 후 자동 만료
- 로그에 민감한 정보 기록 금지

### Rate Limiting
```python
# 향후 구현 예정
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # IP별 요청 횟수 제한
    pass
```

## 📊 성능 메트릭

### 응답 시간 목표
- 일반 대화: < 1초
- 사주 계산: < 3초
- 복잡한 해석: < 5초

### 처리량 목표
- 동시 요청: 100개
- 초당 요청: 50개

## 🔄 세션 관리

### 세션 생명주기
1. **생성**: 첫 번째 요청 시 또는 명시적 session_id 제공 시
2. **유지**: 사용자 활동이 있는 동안 지속
3. **만료**: 30분간 비활성 후 자동 만료
4. **삭제**: 명시적 삭제 요청 또는 만료 후 정리

### 세션 데이터
- 사용자 생년월일시 정보
- 계산된 사주 데이터
- 대화 컨텍스트
- 마지막 활동 시간

## 🧪 테스트 가이드

### 단위 테스트
```bash
# API 엔드포인트 테스트
pytest tests/test_api.py -v
```

### 통합 테스트
```bash
# 전체 워크플로우 테스트
python test_saju.py
```

### 부하 테스트
```bash
# locust 또는 artillery 사용
artillery quick --count 100 --num 10 http://localhost:8000/chat/
```

## 📈 모니터링

### 로그 레벨
- INFO: 일반적인 요청/응답 정보
- WARNING: 예상치 못한 상황
- ERROR: 오류 발생 시

### 메트릭 수집
```python
# 향후 구현 예정
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

---

**다음 문서**: [P05: 핵심 모듈](p05_core_modules.md)
**관련 문서**: [P07: 테스팅 가이드](p07_testing_guide.md)