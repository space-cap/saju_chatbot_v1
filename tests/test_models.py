"""
Pydantic 모델 테스트
"""

import pytest
from pydantic import ValidationError
from app import ChatRequest


class TestChatRequest:
    """ChatRequest 모델 테스트"""

    def test_valid_chat_request(self):
        """유효한 ChatRequest 생성 테스트"""
        # Given
        data = {
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "message": "안녕하세요",
            "history": []
        }

        # When
        request = ChatRequest(**data)

        # Then
        assert request.user_id == "test-user-123"
        assert request.session_id == "test-session-456"
        assert request.message == "안녕하세요"
        assert request.history == []

    def test_chat_request_without_session_id(self):
        """세션 ID 없는 ChatRequest 생성 테스트"""
        # Given
        data = {
            "user_id": "test-user-123",
            "message": "안녕하세요",
            "history": []
        }

        # When
        request = ChatRequest(**data)

        # Then
        assert request.user_id == "test-user-123"
        assert request.session_id is None
        assert request.message == "안녕하세요"
        assert request.history == []

    def test_chat_request_without_history(self):
        """히스토리 없는 ChatRequest 생성 테스트"""
        # Given
        data = {
            "user_id": "test-user-123",
            "message": "안녕하세요"
        }

        # When
        request = ChatRequest(**data)

        # Then
        assert request.user_id == "test-user-123"
        assert request.message == "안녕하세요"
        assert request.history == []  # 기본값

    def test_chat_request_missing_user_id(self):
        """user_id 누락 시 ValidationError 테스트"""
        # Given
        data = {
            "message": "안녕하세요"
        }

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(**data)

        assert "user_id" in str(exc_info.value)

    def test_chat_request_missing_message(self):
        """message 누락 시 ValidationError 테스트"""
        # Given
        data = {
            "user_id": "test-user-123"
        }

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(**data)

        assert "message" in str(exc_info.value)

    def test_chat_request_empty_string_fields(self):
        """빈 문자열 필드 테스트"""
        # Given
        data = {
            "user_id": "",
            "message": "",
            "history": []
        }

        # When
        request = ChatRequest(**data)

        # Then
        assert request.user_id == ""
        assert request.message == ""

    def test_chat_request_with_complex_history(self):
        """복잡한 히스토리가 있는 ChatRequest 테스트"""
        # Given
        complex_history = [
            {
                "role": "user",
                "content": "안녕하세요"
            },
            {
                "role": "assistant",
                "content": "안녕하세요! 무엇을 도와드릴까요?",
                "tool_calls": [
                    {
                        "name": "get_weather",
                        "args": {"location": "서울"},
                        "id": "call-123"
                    }
                ]
            },
            {
                "role": "tool",
                "content": "서울의 날씨는 맑습니다",
                "tool_call_id": "call-123"
            }
        ]

        data = {
            "user_id": "test-user-123",
            "message": "날씨 정보 감사합니다",
            "history": complex_history
        }

        # When
        request = ChatRequest(**data)

        # Then
        assert len(request.history) == 3
        assert request.history[0]["role"] == "user"
        assert request.history[1]["role"] == "assistant"
        assert request.history[2]["role"] == "tool"

    def test_chat_request_unicode_message(self):
        """유니코드 메시지 테스트"""
        # Given
        unicode_messages = [
            "안녕하세요 😊",
            "こんにちは",
            "🌟사주팔자🌟",
            "Привет",
            "🔮✨💫"
        ]

        for message in unicode_messages:
            # When
            data = {
                "user_id": "test-user-123",
                "message": message
            }
            request = ChatRequest(**data)

            # Then
            assert request.message == message

    def test_chat_request_long_fields(self):
        """긴 필드값 테스트"""
        # Given
        long_user_id = "a" * 1000
        long_message = "안녕하세요! " * 500
        long_session_id = "session-" + "x" * 1000

        data = {
            "user_id": long_user_id,
            "session_id": long_session_id,
            "message": long_message
        }

        # When
        request = ChatRequest(**data)

        # Then
        assert len(request.user_id) == 1000
        assert len(request.session_id) == 1008  # "session-" + 1000 chars
        assert len(request.message) > 5000