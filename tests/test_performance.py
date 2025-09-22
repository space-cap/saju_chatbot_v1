"""
성능 및 스트레스 테스트
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from unittest.mock import Mock
from langchain_core.messages import AIMessage


class TestAPIPerformance:
    """API 성능 테스트"""

    @pytest.mark.asyncio
    async def test_single_request_response_time(self, client: AsyncClient, mock_saju_graph):
        """단일 요청 응답 시간 테스트"""
        # Given
        request = {
            "user_id": "perf-test-user",
            "message": "성능 테스트입니다",
            "history": []
        }

        mock_ai_message = Mock()
        mock_ai_message.content = "성능 테스트 응답입니다"
        mock_ai_message.__class__ = AIMessage

        mock_saju_graph.get_graph_app.return_value.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "perf-session"
        }

        # When
        start_time = time.time()
        response = await client.post("/chat/", json=request)
        end_time = time.time()

        # Then
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 5.0  # 5초 이내 응답

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient, mock_saju_graph):
        """동시 요청 처리 테스트"""
        # Given
        num_concurrent_requests = 10

        mock_ai_message = Mock()
        mock_ai_message.content = "동시 요청 처리 응답"
        mock_ai_message.__class__ = AIMessage

        mock_saju_graph.get_graph_app.return_value.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "concurrent-session"
        }

        async def make_request(user_id: str):
            request = {
                "user_id": f"concurrent-user-{user_id}",
                "message": f"동시 요청 테스트 {user_id}",
                "history": []
            }
            return await client.post("/chat/", json=request)

        # When
        start_time = time.time()
        tasks = [make_request(str(i)) for i in range(num_concurrent_requests)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Then
        total_time = end_time - start_time
        assert len(responses) == num_concurrent_requests
        assert all(r.status_code == 200 for r in responses)
        assert total_time < 10.0  # 10초 이내에 모든 요청 완료

    @pytest.mark.asyncio
    async def test_large_payload_handling(self, client: AsyncClient, mock_saju_graph):
        """큰 페이로드 처리 테스트"""
        # Given
        large_history = []
        for i in range(100):  # 100개의 대화 기록
            large_history.extend([
                {"role": "user", "content": f"사용자 메시지 {i}: " + "내용 " * 100},
                {"role": "assistant", "content": f"어시스턴트 응답 {i}: " + "응답 " * 100}
            ])

        request = {
            "user_id": "large-payload-user",
            "message": "큰 페이로드 테스트: " + "데이터 " * 1000,
            "history": large_history
        }

        mock_ai_message = Mock()
        mock_ai_message.content = "큰 페이로드 처리 완료"
        mock_ai_message.__class__ = AIMessage

        mock_saju_graph.get_graph_app.return_value.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "large-payload-session"
        }

        # When
        start_time = time.time()
        response = await client.post("/chat/", json=request)
        end_time = time.time()

        # Then
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 10.0  # 10초 이내 처리

    @pytest.mark.asyncio
    async def test_memory_usage_with_long_conversation(self, client: AsyncClient, mock_saju_graph):
        """긴 대화에서 메모리 사용량 테스트"""
        # Given
        session_id = "memory-test-session"
        conversation_history = []

        mock_ai_message = Mock()
        mock_ai_message.content = "메모리 테스트 응답"
        mock_ai_message.__class__ = AIMessage

        mock_saju_graph.get_graph_app.return_value.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": session_id
        }

        # When & Then - 50번의 연속 대화
        for i in range(50):
            request = {
                "user_id": "memory-test-user",
                "session_id": session_id,
                "message": f"메모리 테스트 메시지 {i}",
                "history": conversation_history
            }

            response = await client.post("/chat/", json=request)
            assert response.status_code == 200

            # 대화 기록 업데이트
            conversation_history = response.json()["full_history"]

        # 최종 검증
        assert len(conversation_history) > 0


class TestAPIStress:
    """API 스트레스 테스트"""

    @pytest.mark.asyncio
    @pytest.mark.slow  # 느린 테스트로 마킹
    async def test_sustained_load(self, client: AsyncClient, mock_saju_graph):
        """지속적인 부하 테스트"""
        # Given
        duration_seconds = 30  # 30초 동안
        request_interval = 0.1  # 0.1초마다 요청

        mock_ai_message = Mock()
        mock_ai_message.content = "부하 테스트 응답"
        mock_ai_message.__class__ = AIMessage

        mock_saju_graph.get_graph_app.return_value.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "stress-session"
        }

        successful_requests = 0
        failed_requests = 0
        start_time = time.time()

        # When
        while time.time() - start_time < duration_seconds:
            try:
                request = {
                    "user_id": f"stress-user-{successful_requests}",
                    "message": "스트레스 테스트",
                    "history": []
                }

                response = await client.post("/chat/", json=request)

                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1

                await asyncio.sleep(request_interval)

            except Exception:
                failed_requests += 1
                await asyncio.sleep(request_interval)

        # Then
        total_requests = successful_requests + failed_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0

        assert total_requests > 0
        assert success_rate > 0.95  # 95% 이상 성공률

    @pytest.mark.asyncio
    async def test_error_recovery(self, client: AsyncClient, mock_saju_graph):
        """오류 복구 테스트"""
        # Given - 처음에는 오류 발생하도록 설정
        mock_saju_graph.get_graph_app.return_value.invoke.side_effect = Exception("Temporary failure")

        request = {
            "user_id": "recovery-test-user",
            "message": "오류 복구 테스트",
            "history": []
        }

        # When - 첫 번째 요청 (실패해야 함)
        response1 = await client.post("/chat/", json=request)

        # Then - 오류 응답 확인
        assert response1.status_code == 500

        # Given - 이제 정상 동작하도록 변경
        mock_ai_message = Mock()
        mock_ai_message.content = "복구된 응답"
        mock_ai_message.__class__ = AIMessage

        mock_saju_graph.get_graph_app.return_value.invoke.side_effect = None
        mock_saju_graph.get_graph_app.return_value.invoke.return_value = {
            "messages": [mock_ai_message],
            "session_id": "recovery-session"
        }

        # When - 두 번째 요청 (성공해야 함)
        response2 = await client.post("/chat/", json=request)

        # Then - 정상 응답 확인
        assert response2.status_code == 200
        data = response2.json()
        assert data["response"] == "복구된 응답"


class TestAPIScalability:
    """API 확장성 테스트"""

    @pytest.mark.asyncio
    async def test_multiple_sessions_simultaneously(self, client: AsyncClient, mock_saju_graph):
        """다중 세션 동시 처리 테스트"""
        # Given
        num_sessions = 20

        mock_ai_message = Mock()
        mock_ai_message.content = "다중 세션 응답"
        mock_ai_message.__class__ = AIMessage

        def mock_invoke(state):
            session_id = state.get("session_id", "default")
            return {
                "messages": [mock_ai_message],
                "session_id": session_id
            }

        mock_saju_graph.get_graph_app.return_value.invoke.side_effect = mock_invoke

        async def simulate_session(session_num: int):
            session_id = f"scalability-session-{session_num}"
            responses = []

            # 각 세션에서 5번의 대화
            for msg_num in range(5):
                request = {
                    "user_id": f"scale-user-{session_num}",
                    "session_id": session_id,
                    "message": f"세션 {session_num}, 메시지 {msg_num}",
                    "history": []
                }
                response = await client.post("/chat/", json=request)
                responses.append(response)

            return responses

        # When
        start_time = time.time()
        session_tasks = [simulate_session(i) for i in range(num_sessions)]
        session_results = await asyncio.gather(*session_tasks)
        end_time = time.time()

        # Then
        total_time = end_time - start_time
        total_requests = sum(len(session_responses) for session_responses in session_results)

        assert len(session_results) == num_sessions
        assert total_requests == num_sessions * 5
        assert all(
            all(r.status_code == 200 for r in session_responses)
            for session_responses in session_results
        )
        assert total_time < 30.0  # 30초 이내에 모든 세션 완료