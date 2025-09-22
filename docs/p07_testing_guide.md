# P07: 테스팅 가이드 (Testing Guide)

## 🧪 테스트 전략

사주 챗봇 시스템은 다층적 테스트 전략을 채택하여 높은 코드 품질과 안정성을 보장합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    테스트 피라미드                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│           E2E Tests (10%)                                   │
│       ┌─────────────────────┐                               │
│       │ 전체 사용자 시나리오    │                               │
│       └─────────────────────┘                               │
│                                                             │
│               Integration Tests (20%)                       │
│           ┌───────────────────────────────┐                 │
│           │ API, Database, LangGraph      │                 │
│           └───────────────────────────────┘                 │
│                                                             │
│                   Unit Tests (70%)                          │
│       ┌─────────────────────────────────────────────┐       │
│       │ 개별 함수, 클래스, 모듈 테스트                │       │
│       └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 테스트 원칙
- **빠른 피드백**: 단위 테스트는 즉각적 실행
- **격리성**: 각 테스트는 독립적으로 실행 가능
- **반복성**: 동일한 입력에 대해 동일한 결과 보장
- **한국어 특화**: 한국 전통 명리학 로직의 정확성 검증

## 🏗️ 테스트 환경 설정

### pytest 설정
```python
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts =
    -ra
    -q
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=80

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    korean: marks tests for Korean language specific features
```

### 테스트 디렉토리 구조
```
tests/
├── conftest.py                    # pytest 설정 및 픽스처
├── unit/                          # 단위 테스트
│   ├── test_saju_calculator.py
│   ├── test_saju_analyzer.py
│   ├── test_saju_interpreter.py
│   └── test_utils.py
├── integration/                   # 통합 테스트
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   ├── test_langraph_workflow.py
│   └── test_knowledge_search.py
├── e2e/                          # E2E 테스트
│   ├── test_complete_consultation.py
│   └── test_user_journey.py
├── fixtures/                     # 테스트 데이터
│   ├── sample_birth_data.json
│   ├── expected_saju_results.json
│   └── mock_llm_responses.json
└── performance/                  # 성능 테스트
    ├── test_load_testing.py
    └── test_memory_usage.py
```

## 🔧 픽스처 및 모킹

### conftest.py 설정
```python
# tests/conftest.py
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import json
import os

from core.saju_calculator import SajuCalculator
from core.saju_analyzer import SajuAnalyzer
from core.saju_interpreter import SajuInterpreter
from database.mysql_manager import MySQLManager
from database.chroma_manager import ChromaManager


@pytest.fixture
def sample_birth_datetime():
    """샘플 생년월일시"""
    return datetime(1990, 5, 15, 14, 30)


@pytest.fixture
def sample_saju_data():
    """샘플 사주 데이터"""
    return {
        'year_ganji': '庚午',
        'month_ganji': '辛巳',
        'day_ganji': '甲子',
        'time_ganji': '辛未',
        'solar_date': datetime(1990, 5, 15, 14, 30),
        'lunar_date': {
            'lunar_year': 1990,
            'lunar_month': 4,
            'lunar_day': 21,
            'is_leap_month': False
        },
        'season': '春',
        'jieqi': '立夏'
    }


@pytest.fixture
def sample_analyzed_saju():
    """샘플 분석된 사주 데이터"""
    return {
        'day_gan': '甲',
        'ohang_counts': {'木': 3, '火': 1, '土': 2, '金': 1, '水': 1},
        'ohang_strength': {'木': 'strong', '火': 'weak', '土': 'neutral'},
        'shipsung': {
            '比肩': ['甲'], '劫財': ['乙'], '食神': ['丙'],
            '傷官': ['丁'], '偏財': ['戊'], '正財': ['己'],
            '偏官': ['庚'], '正官': ['辛'], '偏印': ['壬'], '正印': ['癸']
        },
        'yongshin': '火',
        'gishin': '水',
        'sinsal': ['天乙貴人', '桃花']
    }


@pytest.fixture
def mock_openai_client():
    """OpenAI 클라이언트 모킹"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="안녕하세요! 사주를 봐드리겠습니다."))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_mysql_manager():
    """MySQL 매니저 모킹"""
    mock_manager = Mock(spec=MySQLManager)
    mock_manager.get_user_session.return_value = None
    mock_manager.save_user_session.return_value = True
    mock_manager.save_saju_calculation.return_value = True
    return mock_manager


@pytest.fixture
def mock_chroma_manager():
    """ChromaDB 매니저 모킹"""
    mock_manager = Mock(spec=ChromaManager)
    mock_manager.search_knowledge.return_value = [
        {
            'content': '갑목은 큰 나무의 성질을 가집니다.',
            'metadata': {'category': 'ganzhi', 'element': 'wood'}
        }
    ]
    return mock_manager


@pytest.fixture(scope="session")
def test_database():
    """테스트용 데이터베이스 설정"""
    # 테스트용 SQLite 데이터베이스 생성
    import tempfile
    import sqlite3

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    conn = sqlite3.connect(temp_db.name)

    # 테스트 스키마 생성
    with open('tests/fixtures/test_schema.sql', 'r') as f:
        conn.executescript(f.read())

    yield temp_db.name

    # 정리
    conn.close()
    os.unlink(temp_db.name)


@pytest.fixture
def korean_test_cases():
    """한국어 특화 테스트 케이스"""
    with open('tests/fixtures/korean_test_cases.json', 'r', encoding='utf-8') as f:
        return json.load(f)
```

## 🔬 단위 테스트

### SajuCalculator 테스트
```python
# tests/unit/test_saju_calculator.py
import pytest
from datetime import datetime
from core.saju_calculator import SajuCalculator


class TestSajuCalculator:
    def setup_method(self):
        self.calculator = SajuCalculator()

    def test_calculate_saju_basic(self, sample_birth_datetime):
        """기본 사주 계산 테스트"""
        result = self.calculator.calculate_saju(sample_birth_datetime)

        # 기본 구조 검증
        assert isinstance(result, dict)
        assert 'year_ganji' in result
        assert 'month_ganji' in result
        assert 'day_ganji' in result
        assert 'time_ganji' in result

        # 천간지지 형식 검증
        assert len(result['year_ganji']) == 2
        assert len(result['month_ganji']) == 2
        assert len(result['day_ganji']) == 2
        assert len(result['time_ganji']) == 2

    def test_ganzhi_validity(self, sample_birth_datetime):
        """천간지지 유효성 테스트"""
        result = self.calculator.calculate_saju(sample_birth_datetime)

        # 유효한 천간지지인지 확인
        valid_gan = '甲乙丙丁戊己庚辛壬癸'
        valid_zhi = '子丑寅卯辰巳午未申酉戌亥'

        for ganji_key in ['year_ganji', 'month_ganji', 'day_ganji', 'time_ganji']:
            ganji = result[ganji_key]
            assert ganji[0] in valid_gan, f"Invalid gan in {ganji_key}: {ganji[0]}"
            assert ganji[1] in valid_zhi, f"Invalid zhi in {ganji_key}: {ganji[1]}"

    def test_lunar_conversion(self):
        """음력 변환 테스트"""
        solar_date = datetime(1990, 5, 15)
        lunar_result = self.calculator.get_lunar_date(solar_date)

        assert 'lunar_year' in lunar_result
        assert 'lunar_month' in lunar_result
        assert 'lunar_day' in lunar_result
        assert 'is_leap_month' in lunar_result
        assert isinstance(lunar_result['is_leap_month'], bool)

    @pytest.mark.parametrize("year,month,day,hour,expected_year_gan", [
        (1990, 5, 15, 14, '庚'),  # 경오년
        (1991, 3, 20, 10, '辛'),  # 신미년
        (2000, 1, 1, 0, '己'),    # 기묘년
    ])
    def test_year_gan_calculation(self, year, month, day, hour, expected_year_gan):
        """년간 계산 테스트"""
        birth_time = datetime(year, month, day, hour)
        result = self.calculator.calculate_saju(birth_time)
        assert result['year_ganji'][0] == expected_year_gan

    def test_jieqi_calculation(self):
        """절기 계산 테스트"""
        # 입하 절기 테스트 (5월 5일 경)
        spring_date = datetime(1990, 5, 6)
        result = self.calculator.calculate_saju(spring_date)
        assert result['jieqi'] in ['穀雨', '立夏']

    def test_edge_cases(self):
        """경계값 테스트"""
        # 윤년 2월 29일
        leap_year_date = datetime(2000, 2, 29, 12, 0)
        result = self.calculator.calculate_saju(leap_year_date)
        assert result is not None

        # 자정
        midnight = datetime(1990, 1, 1, 0, 0)
        result = self.calculator.calculate_saju(midnight)
        assert result['time_ganji'][1] == '子'  # 자시

    def test_invalid_input(self):
        """잘못된 입력 테스트"""
        with pytest.raises(ValueError):
            self.calculator.calculate_saju("invalid_date")

    @pytest.mark.korean
    def test_korean_calendar_accuracy(self):
        """한국 전통 역법 정확성 테스트"""
        # 알려진 정확한 사주 데이터와 비교
        known_cases = [
            {
                'birth': datetime(1990, 5, 15, 14, 30),
                'expected': {
                    'year_ganji': '庚午',
                    'day_ganji': '甲子'
                }
            }
        ]

        for case in known_cases:
            result = self.calculator.calculate_saju(case['birth'])
            for key, expected_value in case['expected'].items():
                assert result[key] == expected_value
```

### SajuAnalyzer 테스트
```python
# tests/unit/test_saju_analyzer.py
import pytest
from core.saju_analyzer import SajuAnalyzer


class TestSajuAnalyzer:
    def setup_method(self):
        self.analyzer = SajuAnalyzer()

    def test_analyze_saju_structure(self, sample_saju_data):
        """사주 분석 결과 구조 테스트"""
        result = self.analyzer.analyze_saju(sample_saju_data)

        required_keys = [
            'day_gan', 'ohang_counts', 'ohang_strength',
            'shipsung', 'yongshin', 'gishin', 'sinsal'
        ]

        for key in required_keys:
            assert key in result

    def test_ohang_analysis(self):
        """오행 분석 테스트"""
        test_ganzhi = ['甲子', '乙丑', '丙寅', '丁卯']  # 목목 화화
        result = self.analyzer.analyze_ohang(test_ganzhi)

        assert result['counts']['木'] == 2
        assert result['counts']['火'] == 2
        assert result['dominant'] in ['木', '火']

    def test_shipsung_analysis(self):
        """십성 분석 테스트"""
        day_gan = '甲'
        other_gans = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

        result = self.analyzer.analyze_shipsung(day_gan, other_gans)

        # 모든 십성이 분류되었는지 확인
        all_shipsung = ['比肩', '劫財', '食神', '傷官', '偏財', '正財',
                       '偏官', '正官', '偏印', '正印']

        for shipsung in all_shipsung:
            assert shipsung in result

    def test_sinsal_detection(self, sample_saju_data):
        """신살 감지 테스트"""
        result = self.analyzer.analyze_sinsal(sample_saju_data)

        assert isinstance(result, list)
        # 알려진 신살이 정확히 감지되는지 확인
        for sinsal in result:
            assert sinsal in ['天乙貴人', '文昌貴人', '驛馬', '桃花', '空亡']

    @pytest.mark.parametrize("day_gan,target_gan,expected_shipsung", [
        ('甲', '甲', '比肩'),
        ('甲', '乙', '劫財'),
        ('甲', '丙', '食神'),
        ('甲', '丁', '傷官'),
        ('甲', '戊', '偏財'),
        ('甲', '己', '正財'),
        ('甲', '庚', '偏官'),
        ('甲', '辛', '正官'),
        ('甲', '壬', '偏印'),
        ('甲', '癸', '正印'),
    ])
    def test_shipsung_relations(self, day_gan, target_gan, expected_shipsung):
        """십성 관계 테스트"""
        result = self.analyzer.get_shipsung_relation(day_gan, target_gan)
        assert result == expected_shipsung

    def test_yongshin_gishin_logic(self, sample_analyzed_saju):
        """용신/기신 논리 테스트"""
        yongshin = sample_analyzed_saju['yongshin']
        gishin = sample_analyzed_saju['gishin']

        # 용신과 기신은 서로 다른 오행이어야 함
        assert yongshin != gishin

        # 유효한 오행인지 확인
        valid_ohang = ['木', '火', '土', '金', '水']
        assert yongshin in valid_ohang
        assert gishin in valid_ohang
```

## 🔗 통합 테스트

### API 엔드포인트 테스트
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from app import app


class TestChatAPI:
    def setup_method(self):
        self.client = TestClient(app)

    def test_chat_endpoint_basic(self):
        """기본 채팅 API 테스트"""
        request_data = {
            "user_id": "test_user_123",
            "message": "안녕하세요",
            "history": []
        }

        with patch('chatbot.graph.SajuChatbotGraph') as mock_graph:
            # 모킹된 응답 설정
            mock_graph_app = mock_graph.return_value.get_graph_app.return_value
            mock_graph_app.invoke.return_value = {
                "messages": [
                    {"role": "assistant", "content": "안녕하세요! 사주를 봐드리겠습니다."}
                ]
            }

            response = self.client.post("/chat/", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert "response" in data
            assert "full_history" in data

    def test_saju_calculation_workflow(self):
        """사주 계산 워크플로우 테스트"""
        birth_message = "1990년 5월 15일 오후 2시 30분에 태어났습니다"

        request_data = {
            "user_id": "test_user_123",
            "message": birth_message,
            "history": []
        }

        with patch('core.saju_calculator.SajuCalculator') as mock_calc, \
             patch('core.saju_analyzer.SajuAnalyzer') as mock_analyzer:

            # 모킹 설정
            mock_calc.return_value.calculate_saju.return_value = {
                'year_ganji': '庚午', 'month_ganji': '辛巳',
                'day_ganji': '甲子', 'time_ganji': '辛未'
            }

            response = self.client.post("/chat/", json=request_data)

            assert response.status_code == 200
            # 사주 계산이 호출되었는지 확인
            mock_calc.return_value.calculate_saju.assert_called_once()

    def test_error_handling(self):
        """에러 처리 테스트"""
        # 잘못된 요청 형식
        invalid_request = {"invalid": "data"}

        response = self.client.post("/chat/", json=invalid_request)
        assert response.status_code == 422

    def test_session_persistence(self):
        """세션 지속성 테스트"""
        session_id = "test_session_123"

        # 첫 번째 메시지
        request1 = {
            "user_id": "test_user_123",
            "session_id": session_id,
            "message": "안녕하세요",
            "history": []
        }

        response1 = self.client.post("/chat/", json=request1)
        assert response1.status_code == 200

        # 두 번째 메시지 (같은 세션)
        request2 = {
            "user_id": "test_user_123",
            "session_id": session_id,
            "message": "제 운세를 알려주세요",
            "history": response1.json()["full_history"]
        }

        response2 = self.client.post("/chat/", json=request2)
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
```

### LangGraph 워크플로우 테스트
```python
# tests/integration/test_langraph_workflow.py
import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage

from chatbot.graph import SajuChatbotGraph
from chatbot.state import AgentState


class TestLangGraphWorkflow:
    def setup_method(self):
        self.graph = SajuChatbotGraph()

    def test_workflow_initialization(self):
        """워크플로우 초기화 테스트"""
        graph_app = self.graph.get_graph_app()
        assert graph_app is not None

    @patch('chatbot.tools.calculate_saju_tool')
    @patch('openai.OpenAI')
    def test_complete_workflow(self, mock_openai, mock_saju_tool):
        """완전한 워크플로우 테스트"""
        # 모킹 설정
        mock_openai.return_value.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="사주를 계산해드리겠습니다.", tool_calls=[
                Mock(id="call_123", function=Mock(name="calculate_saju", arguments='{}'))
            ]))
        ]

        mock_saju_tool.return_value = "사주 계산 완료"

        # 초기 상태
        initial_state = {
            "messages": [HumanMessage(content="1990년 5월 15일생 사주를 알려주세요")],
            "session_id": "test_session",
            "user_birth_datetime": None
        }

        graph_app = self.graph.get_graph_app()
        result = graph_app.invoke(initial_state)

        assert "messages" in result
        assert len(result["messages"]) > 1

    def test_state_transitions(self):
        """상태 전이 테스트"""
        from chatbot.graph import call_llm, route_decision

        # call_llm 테스트
        test_state = AgentState(
            messages=[HumanMessage(content="안녕하세요")],
            session_id="test"
        )

        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value.choices = [
                Mock(message=Mock(content="안녕하세요!", tool_calls=None))
            ]

            result = call_llm(test_state)
            assert isinstance(result["messages"][-1], AIMessage)

    def test_tool_calling_flow(self):
        """도구 호출 플로우 테스트"""
        from chatbot.graph import call_tool

        # 도구 호출이 있는 상태
        test_state = AgentState(
            messages=[
                HumanMessage(content="사주를 계산해주세요"),
                AIMessage(content="", tool_calls=[
                    Mock(id="call_123", function=Mock(name="calculate_saju", arguments='{}'))
                ])
            ],
            session_id="test"
        )

        with patch('chatbot.tools.calculate_saju_tool') as mock_tool:
            mock_tool.return_value = "사주 계산 결과"

            result = call_tool(test_state)
            assert len(result["messages"]) > 2
```

## 🌐 E2E 테스트

### 완전한 사용자 여정 테스트
```python
# tests/e2e/test_complete_consultation.py
import pytest
from fastapi.testclient import TestClient
from app import app


class TestCompleteConsultation:
    def setup_method(self):
        self.client = TestClient(app)

    @pytest.mark.e2e
    def test_full_saju_consultation(self):
        """완전한 사주 상담 시나리오"""
        user_id = "e2e_test_user"

        # 1단계: 인사
        response1 = self.client.post("/chat/", json={
            "user_id": user_id,
            "message": "안녕하세요, 사주를 봐주세요",
            "history": []
        })

        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        history = response1.json()["full_history"]

        # 2단계: 생년월일시 제공
        response2 = self.client.post("/chat/", json={
            "user_id": user_id,
            "session_id": session_id,
            "message": "1990년 5월 15일 오후 2시 30분에 태어났습니다",
            "history": history
        })

        assert response2.status_code == 200
        assert "庚" in response2.json()["response"] or "사주" in response2.json()["response"]
        history = response2.json()["full_history"]

        # 3단계: 구체적 질문
        response3 = self.client.post("/chat/", json={
            "user_id": user_id,
            "session_id": session_id,
            "message": "올해 재물운은 어떤가요?",
            "history": history
        })

        assert response3.status_code == 200
        assert "재물" in response3.json()["response"] or "운" in response3.json()["response"]

    @pytest.mark.e2e
    def test_error_recovery(self):
        """오류 복구 시나리오"""
        # 잘못된 생년월일시 입력
        response = self.client.post("/chat/", json={
            "user_id": "error_test_user",
            "message": "1990년 99월 99일에 태어났습니다",
            "history": []
        })

        assert response.status_code == 200
        # 시스템이 적절한 오류 메시지를 반환하는지 확인
        assert "다시" in response.json()["response"] or "확인" in response.json()["response"]
```

## ⚡ 성능 테스트

### 로드 테스트
```python
# tests/performance/test_load_testing.py
import pytest
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import statistics


class TestPerformance:
    @pytest.mark.slow
    def test_concurrent_requests(self):
        """동시 요청 처리 성능 테스트"""
        base_url = "http://localhost:8000"
        num_requests = 50
        concurrent_users = 10

        async def make_request(session, user_id):
            start_time = time.time()
            async with session.post(f"{base_url}/chat/", json={
                "user_id": f"perf_user_{user_id}",
                "message": "안녕하세요",
                "history": []
            }) as response:
                await response.json()
                return time.time() - start_time

        async def run_test():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(num_requests):
                    user_id = i % concurrent_users
                    tasks.append(make_request(session, user_id))

                response_times = await asyncio.gather(*tasks)
                return response_times

        response_times = asyncio.run(run_test())

        # 성능 검증
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95 percentile

        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time}s"
        assert p95_response_time < 5.0, f"95th percentile too high: {p95_response_time}s"

    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # 다수의 사주 계산 수행
        from core.saju_calculator import SajuCalculator
        from datetime import datetime

        calculator = SajuCalculator()

        for i in range(100):
            birth_time = datetime(1990 + i % 30, (i % 12) + 1, (i % 28) + 1, 12, 0)
            calculator.calculate_saju(birth_time)

        gc.collect()  # 가비지 컬렉션 강제 실행
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 메모리 증가량이 합리적 범위 내인지 확인 (100MB 이하)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increase too high: {memory_increase / 1024 / 1024:.2f}MB"
```

## 📊 테스트 커버리지

### 커버리지 설정
```python
# .coveragerc
[run]
source = .
omit =
    tests/*
    playground/*
    .venv/*
    */__pycache__/*
    */migrations/*
    manage.py
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\(Protocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
```

### 커버리지 리포트 생성
```bash
# 커버리지 실행
pytest --cov=. --cov-report=html --cov-report=term-missing

# 커버리지 목표: 80% 이상
pytest --cov=. --cov-fail-under=80
```

## 🤖 테스트 자동화

### GitHub Actions 워크플로우
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: saju_chatbot_test
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-cov pytest-asyncio

    - name: Run unit tests
      run: pytest tests/unit/ -v --cov=core --cov-report=xml

    - name: Run integration tests
      run: pytest tests/integration/ -v
      env:
        MYSQL_HOST: localhost
        MYSQL_USER: root
        MYSQL_PASSWORD: test_password
        MYSQL_DB: saju_chatbot_test

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 테스트 실행 스크립트
```bash
#!/bin/bash
# run_all_tests.sh

echo "🧪 Running Saju Chatbot Test Suite"

# 단위 테스트
echo "📝 Running unit tests..."
pytest tests/unit/ -v --cov=core --cov=chatbot --cov=database

# 통합 테스트
echo "🔗 Running integration tests..."
pytest tests/integration/ -v

# E2E 테스트 (옵션)
if [ "$RUN_E2E" = "true" ]; then
    echo "🌐 Running E2E tests..."
    pytest tests/e2e/ -v
fi

# 성능 테스트 (옵션)
if [ "$RUN_PERFORMANCE" = "true" ]; then
    echo "⚡ Running performance tests..."
    pytest tests/performance/ -v -m slow
fi

echo "✅ All tests completed!"
```

## 🔍 디버깅 및 문제 해결

### 테스트 디버깅
```python
# pytest 디버깅 옵션
pytest -v -s --pdb tests/unit/test_saju_calculator.py::TestSajuCalculator::test_calculate_saju_basic

# 특정 마커만 실행
pytest -m "korean and not slow"

# 실패한 테스트만 재실행
pytest --lf

# 커스텀 마커로 테스트 분류
pytest -m "integration"
```

### 로그 기반 디버깅
```python
# 테스트 중 로깅 활성화
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_debug_logging():
    logger = logging.getLogger(__name__)
    logger.debug("테스트 시작")

    # 테스트 코드

    logger.debug("테스트 완료")
```

---

**다음 문서**: [P08: 배포 가이드](p08_deployment.md)
**관련 문서**: [P02: 개발환경 설정](p02_setup_guide.md)