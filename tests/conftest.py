"""
pytest 설정 및 공통 fixtures
"""

import pytest
import pytest_asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# app.py를 import하기 전에 필요한 모듈들을 미리 mock 처리
sys.modules['mysql.connector'] = MagicMock()
sys.modules['mysql.connector.Error'] = Exception
sys.modules['database.mysql_manager'] = MagicMock()
sys.modules['database.chroma_manager'] = MagicMock()
sys.modules['chatbot.graph'] = MagicMock()
sys.modules['chatbot.nodes'] = MagicMock()
sys.modules['chatbot.tools'] = MagicMock()

@pytest.fixture
def mock_mysql_manager():
    """MySQL Manager mock fixture"""
    # app 모듈에서 직접 mysql_manager를 mock
    with patch('app.mysql_manager') as mock_instance:
        mock_instance.get_user_session.return_value = None
        mock_instance.save_user_session.return_value = None
        mock_instance.close.return_value = None
        yield mock_instance

@pytest.fixture
def mock_saju_graph():
    """Saju Graph mock fixture"""
    # app 모듈에서 직접 saju_graph_app을 mock
    with patch('app.saju_graph_app') as mock_app:
        # Mock invoke method to return a proper response structure
        # 실제 AIMessage 인스턴스를 생성
        mock_ai_message = AIMessage(content="안녕하세요! 사주팔자 상담을 도와드리겠습니다.")

        mock_app.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "test-session-id",
            "user_birth_datetime": None,
            "saju_calculated_info": None
        }
        yield mock_app

@pytest.fixture
def client(mock_mysql_manager, mock_saju_graph):
    """Test client fixture for testing FastAPI app"""
    from app import app
    with TestClient(app) as test_client:
        yield test_client

@pytest_asyncio.fixture
async def async_client(mock_mysql_manager, mock_saju_graph):
    """AsyncClient fixture for testing FastAPI app"""
    from app import app
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
def sample_chat_request():
    """Sample chat request data"""
    return {
        "user_id": "test-user-123",
        "session_id": "test-session-456",
        "message": "안녕하세요, 제 사주를 봐주세요",
        "history": []
    }

@pytest.fixture
def sample_chat_request_with_history():
    """Sample chat request with conversation history"""
    return {
        "user_id": "test-user-123",
        "session_id": "test-session-456",
        "message": "제 직업운은 어떤가요?",
        "history": [
            {
                "role": "user",
                "content": "1990년 5월 15일 오후 2시에 태어났습니다"
            },
            {
                "role": "assistant",
                "content": "생년월일시 정보를 확인했습니다. 사주팔자를 계산해보겠습니다."
            }
        ]
    }

@pytest.fixture
def sample_birth_info():
    """Sample birth information"""
    return {
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": 14,
        "is_lunar": False,
        "is_leap_month": False
    }