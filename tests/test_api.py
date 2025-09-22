"""
FastAPI 앱 API 테스트
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import status
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


class TestChatAPI:
    """채팅 API 테스트 클래스"""

    def test_chat_basic_request(self, client, sample_chat_request, mock_saju_graph):
        """기본 채팅 요청 테스트"""
        # Given - mock_saju_graph는 이미 conftest.py에서 설정됨

        # When
        response = client.post("/chat/", json=sample_chat_request)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "session_id" in data
        assert "response" in data
        assert "full_history" in data
        assert data["response"] == "안녕하세요! 사주팔자 상담을 도와드리겠습니다."

    def test_chat_with_history(self, client, sample_chat_request_with_history, mock_saju_graph):
        """대화 기록이 있는 채팅 요청 테스트"""
        # Given
        mock_ai_message = AIMessage(content="직업운에 대해 말씀드리겠습니다.")

        mock_saju_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="1990년 5월 15일 오후 2시에 태어났습니다"),
                AIMessage(content="생년월일시 정보를 확인했습니다."),
                HumanMessage(content="제 직업운은 어떤가요?"),
                mock_ai_message
            ],
            "session_id": "test-session-456",
            "user_birth_datetime": None,
            "saju_calculated_info": None
        }

        # When
        response = client.post("/chat/", json=sample_chat_request_with_history)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["response"] == "직업운에 대해 말씀드리겠습니다."
        assert len(data["full_history"]) == 4  # 대화 기록 4개

    def test_chat_without_session_id(self, client, mock_saju_graph):
        """세션 ID 없이 채팅 요청 테스트 (새 세션 생성)"""
        # Given
        request_without_session = {
            "user_id": "test-user-123",
            "message": "안녕하세요",
            "history": []
        }

        mock_ai_message = AIMessage(content="새로운 세션에서 안녕하세요!")

        mock_saju_graph.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": None,
            "user_birth_datetime": None,
            "saju_calculated_info": None
        }

        # When
        response = client.post("/chat/", json=request_without_session)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "session_id" in data
        assert data["session_id"] is not None  # 새로운 세션 ID가 생성됨
        assert data["response"] == "새로운 세션에서 안녕하세요!"

    def test_chat_with_existing_session_data(self, client, mock_mysql_manager, mock_saju_graph):
        """기존 세션 데이터가 있는 경우 테스트"""
        # Given
        from datetime import datetime

        mock_mysql_manager.get_user_session.return_value = {
            "birth_datetime": datetime(1990, 5, 15, 14, 0),
            "is_lunar": False,
            "is_leap_month": False
        }

        mock_ai_message = AIMessage(content="기존 사주 정보를 바탕으로 답변드리겠습니다.")

        mock_saju_graph.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "existing-session",
            "user_birth_datetime": datetime(1990, 5, 15, 14, 0),
            "user_birth_is_lunar": False,
            "user_birth_is_leap_month": False,
            "saju_calculated_info": {"year_ganji": "庚午"}
        }

        request = {
            "user_id": "test-user-123",
            "session_id": "existing-session",
            "message": "제 운세는 어떤가요?",
            "history": []
        }

        # When
        response = client.post("/chat/", json=request)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["response"] == "기존 사주 정보를 바탕으로 답변드리겠습니다."
        mock_mysql_manager.get_user_session.assert_called_once()
        mock_mysql_manager.save_user_session.assert_called_once()

    def test_chat_tool_message_response(self, client, sample_chat_request, mock_saju_graph):
        """도구 메시지 응답 테스트"""
        # Given
        mock_tool_message = ToolMessage(
            content='{"saju_info": {"year_ganji": "庚午"}}',
            tool_call_id="tool-call-123"
        )

        mock_saju_graph.invoke.return_value = {
            "messages": [mock_tool_message],
            "session_id": "test-session-456",
            "user_birth_datetime": None,
            "saju_calculated_info": None
        }

        # When
        response = client.post("/chat/", json=sample_chat_request)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "Tool Result:" in data["response"]
        assert "saju_info" in data["response"]

    def test_chat_error_handling(self, client, sample_chat_request, mock_saju_graph):
        """에러 핸들링 테스트"""
        # Given
        mock_saju_graph.invoke.side_effect = Exception("Graph execution failed")

        # When
        response = client.post("/chat/", json=sample_chat_request)

        # Then
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Internal Server Error" in data["detail"]

    def test_chat_no_response_message(self, client, sample_chat_request, mock_saju_graph):
        """응답 메시지가 없는 경우 테스트"""
        # Given
        mock_saju_graph.invoke.return_value = {
            "messages": [],
            "session_id": "test-session-456"
        }

        # When
        response = client.post("/chat/", json=sample_chat_request)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["response"] == "죄송합니다. 현재 요청을 처리할 수 없습니다."

    def test_chat_invalid_request_format(self, client):
        """잘못된 요청 형식 테스트"""
        # Given
        invalid_request = {
            "message": "안녕하세요"
            # user_id 누락
        }

        # When
        response = client.post("/chat/", json=invalid_request)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_chat_message_history_conversion(self, client, mock_saju_graph):
        """메시지 히스토리 변환 테스트"""
        # Given
        request_with_tool_calls = {
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "message": "제 사주를 알려주세요",
            "history": [
                {
                    "role": "user",
                    "content": "1990년 5월 15일에 태어났습니다"
                },
                {
                    "role": "assistant",
                    "content": "생년월일을 확인했습니다.",
                    "tool_calls": [{"name": "calculate_saju", "args": {"year": 1990}, "id": "call-123"}]
                },
                {
                    "role": "tool",
                    "content": "계산 완료",
                    "tool_call_id": "call-123"
                }
            ]
        }

        mock_ai_message = Mock()
        mock_ai_message.content = "사주 계산이 완료되었습니다."
        mock_ai_message.__class__ = AIMessage
        mock_ai_message.tool_calls = None

        mock_saju_graph.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "test-session-456"
        }

        # When
        response = client.post("/chat/", json=request_with_tool_calls)

        # Then
        assert response.status_code == status.HTTP_200_OK
        # 호출 인자 확인 (메시지 변환이 제대로 됐는지)
        call_args = mock_saju_graph.invoke.call_args[0][0]
        assert len(call_args["messages"]) == 4  # 히스토리 3개 + 현재 메시지 1개


class TestAPIValidation:
    """API 입력 검증 테스트"""

    def test_empty_message(self, client):
        """빈 메시지 테스트"""
        # Given
        request = {
            "user_id": "test-user-123",
            "message": "",
            "history": []
        }

        # When
        response = client.post("/chat/", json=request)

        # Then
        assert response.status_code == status.HTTP_200_OK  # 빈 메시지도 허용

    def test_long_message(self, client, mock_saju_graph):
        """긴 메시지 테스트"""
        # Given
        long_message = "안녕하세요! " * 1000  # 매우 긴 메시지
        request = {
            "user_id": "test-user-123",
            "message": long_message,
            "history": []
        }

        mock_ai_message = AIMessage(content="긴 메시지를 받았습니다.")

        mock_saju_graph.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": None
        }

        # When
        response = client.post("/chat/", json=request)

        # Then
        assert response.status_code == status.HTTP_200_OK

    def test_special_characters_in_message(self, client, mock_saju_graph):
        """특수 문자가 포함된 메시지 테스트"""
        # Given
        special_message = "안녕하세요! 😊 제 사주를 봐주세요. #사주 @fortune 2024-01-01"
        request = {
            "user_id": "test-user-123",
            "message": special_message,
            "history": []
        }

        mock_ai_message = AIMessage(content="특수 문자가 포함된 메시지를 처리했습니다.")

        mock_saju_graph.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": None
        }

        # When
        response = client.post("/chat/", json=request)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["response"] == "특수 문자가 포함된 메시지를 처리했습니다."


class TestAPIIntegration:
    """API 통합 테스트"""

    def test_full_conversation_flow(self, client, mock_mysql_manager, mock_saju_graph):
        """전체 대화 플로우 테스트"""
        # Given - 첫 번째 메시지
        first_request = {
            "user_id": "integration-test-user",
            "message": "안녕하세요, 사주를 봐주세요",
            "history": []
        }

        mock_ai_message_1 = AIMessage(content="안녕하세요! 생년월일시를 알려주세요.")

        mock_saju_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="안녕하세요, 사주를 봐주세요"),
                mock_ai_message_1
            ],
            "session_id": "integration-session-123"
        }

        # When - 첫 번째 요청
        response1 = client.post("/chat/", json=first_request)

        # Then - 첫 번째 응답 검증
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        session_id = data1["session_id"]

        # Given - 두 번째 메시지 (세션 이어받기)
        second_request = {
            "user_id": "integration-test-user",
            "session_id": session_id,
            "message": "1990년 5월 15일 오후 2시에 태어났습니다",
            "history": data1["full_history"]
        }

        mock_ai_message_2 = AIMessage(content="사주팔자를 계산하겠습니다.")

        mock_saju_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="안녕하세요, 사주를 봐주세요"),
                AIMessage(content="안녕하세요! 생년월일시를 알려주세요."),
                HumanMessage(content="1990년 5월 15일 오후 2시에 태어났습니다"),
                mock_ai_message_2
            ],
            "session_id": session_id,
            "user_birth_datetime": "1990-05-15T14:00:00",
            "user_birth_is_lunar": False,
            "user_birth_is_leap_month": False,
            "saju_calculated_info": {"year_ganji": "庚午"}
        }

        # When - 두 번째 요청
        response2 = client.post("/chat/", json=second_request)

        # Then - 두 번째 응답 검증
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert data2["session_id"] == session_id  # 같은 세션 유지
        assert len(data2["full_history"]) == 4  # 대화 히스토리 누적