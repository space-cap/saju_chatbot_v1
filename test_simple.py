#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 API 테스트 (의존성 최소화)
"""

import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pydantic_models():
    """Pydantic 모델 테스트"""
    print("=== Pydantic 모델 테스트 ===")

    try:
        # Mock all the problematic imports
        sys.modules['mysql.connector'] = MagicMock()
        sys.modules['database.mysql_manager'] = MagicMock()
        sys.modules['database.chroma_manager'] = MagicMock()
        sys.modules['chatbot.graph'] = MagicMock()
        sys.modules['chatbot.nodes'] = MagicMock()
        sys.modules['chatbot.tools'] = MagicMock()

        from app import ChatRequest

        # 유효한 ChatRequest 테스트
        data = {
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "message": "안녕하세요",
            "history": []
        }

        request = ChatRequest(**data)
        assert request.user_id == "test-user-123"
        assert request.session_id == "test-session-456"
        assert request.message == "안녕하세요"
        assert request.history == []
        print("✅ 유효한 ChatRequest 생성 테스트 통과")

        # 세션 ID 없는 경우
        data_no_session = {
            "user_id": "test-user-123",
            "message": "안녕하세요"
        }

        request_no_session = ChatRequest(**data_no_session)
        assert request_no_session.session_id is None
        assert request_no_session.history == []  # 기본값
        print("✅ 세션 ID 없는 ChatRequest 테스트 통과")

        # 유니코드 메시지 테스트
        unicode_data = {
            "user_id": "test-user-123",
            "message": "안녕하세요 😊 사주팔자 🔮"
        }

        unicode_request = ChatRequest(**unicode_data)
        assert "😊" in unicode_request.message
        assert "🔮" in unicode_request.message
        print("✅ 유니코드 메시지 테스트 통과")

        return True

    except Exception as e:
        print(f"❌ Pydantic 모델 테스트 실패: {e}")
        return False

def test_api_request_validation():
    """API 요청 검증 테스트"""
    print("\n=== API 요청 검증 테스트 ===")

    try:
        from pydantic import ValidationError

        # Mock imports
        sys.modules['mysql.connector'] = MagicMock()
        sys.modules['database.mysql_manager'] = MagicMock()
        sys.modules['database.chroma_manager'] = MagicMock()
        sys.modules['chatbot.graph'] = MagicMock()
        sys.modules['chatbot.nodes'] = MagicMock()
        sys.modules['chatbot.tools'] = MagicMock()

        from app import ChatRequest

        # user_id 누락 테스트
        try:
            ChatRequest(message="안녕하세요")
            print("❌ user_id 누락 검증 실패")
            return False
        except ValidationError:
            print("✅ user_id 누락 검증 통과")

        # message 누락 테스트
        try:
            ChatRequest(user_id="test-user")
            print("❌ message 누락 검증 실패")
            return False
        except ValidationError:
            print("✅ message 누락 검증 통과")

        # 빈 문자열 허용 테스트
        empty_request = ChatRequest(user_id="", message="")
        assert empty_request.user_id == ""
        assert empty_request.message == ""
        print("✅ 빈 문자열 필드 테스트 통과")

        return True

    except Exception as e:
        print(f"❌ API 요청 검증 테스트 실패: {e}")
        return False

def test_json_serialization():
    """JSON 직렬화 테스트"""
    print("\n=== JSON 직렬화 테스트 ===")

    try:
        # Mock imports
        sys.modules['mysql.connector'] = MagicMock()
        sys.modules['database.mysql_manager'] = MagicMock()
        sys.modules['database.chroma_manager'] = MagicMock()
        sys.modules['chatbot.graph'] = MagicMock()
        sys.modules['chatbot.nodes'] = MagicMock()
        sys.modules['chatbot.tools'] = MagicMock()

        from app import ChatRequest

        # 복잡한 히스토리 테스트
        complex_history = [
            {"role": "user", "content": "안녕하세요"},
            {
                "role": "assistant",
                "content": "안녕하세요! 무엇을 도와드릴까요?",
                "tool_calls": [{"name": "calculate_saju", "args": {"year": 1990}, "id": "call-123"}]
            },
            {"role": "tool", "content": "계산 완료", "tool_call_id": "call-123"}
        ]

        request = ChatRequest(
            user_id="test-user",
            message="테스트 메시지",
            history=complex_history
        )

        # JSON 직렬화
        json_str = request.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["user_id"] == "test-user"
        assert parsed["message"] == "테스트 메시지"
        assert len(parsed["history"]) == 3
        assert parsed["history"][1]["tool_calls"][0]["name"] == "calculate_saju"

        print("✅ 복잡한 히스토리 JSON 직렬화 테스트 통과")

        return True

    except Exception as e:
        print(f"❌ JSON 직렬화 테스트 실패: {e}")
        return False

def test_large_data_handling():
    """대용량 데이터 처리 테스트"""
    print("\n=== 대용량 데이터 처리 테스트 ===")

    try:
        # Mock imports
        sys.modules['mysql.connector'] = MagicMock()
        sys.modules['database.mysql_manager'] = MagicMock()
        sys.modules['database.chroma_manager'] = MagicMock()
        sys.modules['chatbot.graph'] = MagicMock()
        sys.modules['chatbot.nodes'] = MagicMock()
        sys.modules['chatbot.tools'] = MagicMock()

        from app import ChatRequest

        # 긴 메시지 테스트
        long_message = "안녕하세요! " * 1000
        request = ChatRequest(
            user_id="test-user",
            message=long_message
        )

        assert len(request.message) > 10000
        print("✅ 긴 메시지 처리 테스트 통과")

        # 많은 히스토리 테스트
        large_history = []
        for i in range(100):
            large_history.extend([
                {"role": "user", "content": f"사용자 메시지 {i}"},
                {"role": "assistant", "content": f"어시스턴트 응답 {i}"}
            ])

        large_request = ChatRequest(
            user_id="test-user",
            message="대용량 테스트",
            history=large_history
        )

        assert len(large_request.history) == 200
        print("✅ 대용량 히스토리 처리 테스트 통과")

        return True

    except Exception as e:
        print(f"❌ 대용량 데이터 처리 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("FastAPI 사주 챗봇 API 단순 테스트 시작")
    print("=" * 60)

    tests = [
        test_pydantic_models,
        test_api_request_validation,
        test_json_serialization,
        test_large_data_handling
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 예외 발생: {e}")

    print("\n" + "=" * 60)
    print(f"테스트 결과: {passed}/{total} 통과")

    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
        return True
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)