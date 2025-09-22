#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 환경설정 테스트 스크립트
LLM Configuration Test Script
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_llm_config():
    """LLM 환경설정 테스트"""
    print("LLM 환경설정 테스트 시작...")

    try:
        from config import (
            OPENAI_API_KEY,
            OPENAI_MODEL,
            OPENAI_TEMPERATURE,
            OPENAI_MAX_TOKENS
        )

        print("성공: LLM 환경설정이 로드되었습니다.")
        print()
        print("=== LLM 설정 값 확인 ===")
        print(f"OPENAI_MODEL: {OPENAI_MODEL}")
        print(f"OPENAI_TEMPERATURE: {OPENAI_TEMPERATURE} (타입: {type(OPENAI_TEMPERATURE)})")
        print(f"OPENAI_MAX_TOKENS: {OPENAI_MAX_TOKENS} (타입: {type(OPENAI_MAX_TOKENS)})")
        print(f"OPENAI_API_KEY: {'설정됨' if OPENAI_API_KEY else '설정되지 않음'}")

        # 타입 검증
        assert isinstance(OPENAI_MODEL, str), "OPENAI_MODEL은 문자열이어야 합니다"
        assert isinstance(OPENAI_TEMPERATURE, float), "OPENAI_TEMPERATURE는 float이어야 합니다"
        assert isinstance(OPENAI_MAX_TOKENS, int), "OPENAI_MAX_TOKENS는 int이어야 합니다"
        assert OPENAI_API_KEY, "OPENAI_API_KEY가 설정되어야 합니다"

        print("타입 검증: 모든 설정이 올바른 타입입니다.")

        return True

    except Exception as e:
        print(f"실패: LLM 환경설정 오류 - {e}")
        return False

def test_langchain_openai():
    """LangChain OpenAI 모듈 테스트"""
    print("\nLangChain OpenAI 모듈 테스트 시작...")

    try:
        from langchain_openai import ChatOpenAI
        from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS

        # ChatOpenAI 인스턴스 생성 테스트
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
            api_key=OPENAI_API_KEY
        )

        print("성공: ChatOpenAI 인스턴스가 생성되었습니다.")
        print(f"모델명: {llm.model_name}")
        print(f"온도: {llm.temperature}")
        print(f"최대 토큰: {llm.max_tokens}")

        return True

    except Exception as e:
        print(f"실패: ChatOpenAI 생성 오류 - {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("LLM 환경설정 테스트")
    print("=" * 60)

    # LLM 설정 테스트
    config_success = test_llm_config()

    # LangChain OpenAI 테스트
    langchain_success = test_langchain_openai()

    print("\n" + "=" * 60)
    if config_success and langchain_success:
        print("모든 LLM 설정 테스트가 성공적으로 완료되었습니다!")
        print("환경변수에서 LLM 설정이 올바르게 로드되었습니다.")
    else:
        print("일부 LLM 설정 테스트가 실패했습니다.")
    print("=" * 60)

    return config_success and langchain_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)