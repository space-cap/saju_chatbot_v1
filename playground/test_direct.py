#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 테스트 실행 스크립트
"""

import sys
import os
from unittest.mock import MagicMock

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_directly():
    """모델 직접 테스트"""
    print("=== Pydantic 모델 직접 테스트 ===")

    # Mock problematic modules
    sys.modules['mysql.connector'] = MagicMock()
    sys.modules['database.mysql_manager'] = MagicMock()
    sys.modules['database.chroma_manager'] = MagicMock()
    sys.modules['chatbot.graph'] = MagicMock()
    sys.modules['chatbot.nodes'] = MagicMock()
    sys.modules['chatbot.tools'] = MagicMock()

    try:
        from app import ChatRequest
        from pydantic import ValidationError

        # Test 1: Valid request
        print("1. 유효한 요청 테스트...")
        data = {'user_id': 'test-123', 'message': 'Hello', 'session_id': 'sess-456'}
        req = ChatRequest(**data)
        assert req.user_id == 'test-123'
        assert req.message == 'Hello'
        assert req.session_id == 'sess-456'
        print("   성공: 유효한 요청 처리됨")

        # Test 2: Missing user_id should fail
        print("2. user_id 누락 검증 테스트...")
        try:
            ChatRequest(message='Hello')
            print("   실패: user_id 누락이 허용되면 안됨")
            return False
        except ValidationError:
            print("   성공: user_id 누락 시 ValidationError 발생")

        # Test 3: Missing message should fail
        print("3. message 누락 검증 테스트...")
        try:
            ChatRequest(user_id='test-123')
            print("   실패: message 누락이 허용되면 안됨")
            return False
        except ValidationError:
            print("   성공: message 누락 시 ValidationError 발생")

        # Test 4: Optional session_id
        print("4. 선택적 session_id 테스트...")
        req_no_session = ChatRequest(user_id='test', message='Hi')
        assert req_no_session.session_id is None
        assert req_no_session.history == []  # 기본값
        print("   성공: session_id 없이도 요청 생성됨")

        # Test 5: Unicode handling
        print("5. 유니코드 처리 테스트...")
        unicode_req = ChatRequest(user_id='test', message='안녕하세요 😊 사주팔자 🔮')
        assert '안녕하세요' in unicode_req.message
        assert '😊' in unicode_req.message
        assert '🔮' in unicode_req.message
        print("   성공: 한글과 이모지 처리됨")

        # Test 6: Complex history
        print("6. 복잡한 히스토리 테스트...")
        history = [
            {'role': 'user', 'content': '안녕하세요'},
            {
                'role': 'assistant',
                'content': '안녕하세요!',
                'tool_calls': [{'name': 'test_tool', 'args': {}, 'id': 'call-123'}]
            },
            {'role': 'tool', 'content': '결과', 'tool_call_id': 'call-123'}
        ]
        complex_req = ChatRequest(user_id='test', message='테스트', history=history)
        assert len(complex_req.history) == 3
        assert complex_req.history[0]['role'] == 'user'
        assert complex_req.history[1]['role'] == 'assistant'
        assert complex_req.history[2]['role'] == 'tool'
        print("   성공: 복잡한 대화 히스토리 처리됨")

        # Test 7: Large data
        print("7. 대용량 데이터 테스트...")
        large_message = "테스트 메시지 " * 1000
        large_req = ChatRequest(user_id='test', message=large_message)
        expected_length = len("테스트 메시지 ") * 1000
        assert len(large_req.message) >= expected_length
        print(f"   성공: {len(large_req.message):,}자 메시지 처리됨")

        print("\n모든 Pydantic 모델 테스트 통과!")
        return True

    except Exception as e:
        print(f"   오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_mock():
    """API Mock 테스트"""
    print("\n=== API Mock 테스트 ===")

    try:
        # Mock all external dependencies
        sys.modules['mysql.connector'] = MagicMock()

        # Create mock managers
        mock_mysql = MagicMock()
        mock_mysql.get_user_session.return_value = None
        mock_mysql.save_user_session.return_value = None
        sys.modules['database.mysql_manager'].MySQLManager.return_value = mock_mysql

        mock_chroma = MagicMock()
        sys.modules['database.chroma_manager'].ChromaManager.return_value = mock_chroma

        # Mock graph
        mock_graph_instance = MagicMock()
        mock_app = MagicMock()

        # Mock successful response
        mock_app.invoke.return_value = {
            "messages": [MagicMock(content="테스트 응답입니다")],
            "session_id": "test-session",
            "user_birth_datetime": None,
            "saju_calculated_info": None
        }

        mock_graph_instance.get_graph_app.return_value = mock_app
        sys.modules['chatbot.graph'].SajuChatbotGraph.return_value = mock_graph_instance

        from app import ChatRequest
        print("1. ChatRequest 모델 사용 가능 확인: 성공")

        # Test request creation
        request_data = {
            "user_id": "api-test-user",
            "message": "API 테스트입니다",
            "history": []
        }

        request = ChatRequest(**request_data)
        print("2. API 요청 객체 생성: 성공")
        print(f"   - user_id: {request.user_id}")
        print(f"   - message: {request.message}")

        # Test JSON serialization for API
        json_data = request.model_dump()
        print("3. JSON 직렬화: 성공")
        print(f"   - 직렬화된 키: {list(json_data.keys())}")

        print("\nAPI Mock 테스트 통과!")
        return True

    except Exception as e:
        print(f"   오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print("FastAPI 사주 챗봇 API 직접 테스트")
    print("=" * 60)

    tests = [
        ("Pydantic 모델 테스트", test_model_directly),
        ("API Mock 테스트", test_api_mock)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n[실행중] {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"[통과] {test_name}")
            else:
                print(f"[실패] {test_name}")
        except Exception as e:
            print(f"[예외] {test_name}: {e}")

    print("\n" + "=" * 60)
    print(f"테스트 결과: {passed}/{total} 통과")

    if passed == total:
        print("모든 직접 테스트가 성공했습니다!")
        print("\n이제 다음 명령어로 전체 pytest 실행이 가능합니다:")
        print("  python -m pytest tests/test_models.py -v (모델 테스트)")
        print("  python -m pytest tests/test_api.py -v (API 테스트)")
        return True
    else:
        print("일부 테스트가 실패했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)