#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
환경설정 테스트 스크립트
Configuration Test Script
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """환경설정 로딩 테스트"""
    print("환경설정 로딩 테스트 시작...")

    try:
        from config import (
            OPENAI_API_KEY,
            OPENAI_MODEL,
            OPENAI_TEMPERATURE,
            OPENAI_MAX_TOKENS,
            MYSQL_HOST,
            MYSQL_USER,
            MYSQL_DB,
            CHROMA_PERSIST_DIRECTORY,
            EMBEDDING_MODEL_NAME
        )

        print("성공: 모든 환경설정이 로드되었습니다.")
        print()
        print("=== 설정 값 확인 ===")
        print(f"OPENAI_MODEL: {OPENAI_MODEL}")
        print(f"OPENAI_TEMPERATURE: {OPENAI_TEMPERATURE}")
        print(f"OPENAI_MAX_TOKENS: {OPENAI_MAX_TOKENS}")
        print(f"OPENAI_API_KEY: {'설정됨' if OPENAI_API_KEY else '설정되지 않음'}")
        print()
        print(f"MYSQL_HOST: {MYSQL_HOST}")
        print(f"MYSQL_USER: {MYSQL_USER}")
        print(f"MYSQL_DB: {MYSQL_DB}")
        print()
        print(f"CHROMA_PERSIST_DIRECTORY: {CHROMA_PERSIST_DIRECTORY}")
        print(f"EMBEDDING_MODEL_NAME: {EMBEDDING_MODEL_NAME}")

        return True

    except Exception as e:
        print(f"실패: 환경설정 로드 오류 - {e}")
        return False

def test_tools_loading():
    """도구 모듈 로딩 테스트"""
    print("\n도구 모듈 로딩 테스트 시작...")

    try:
        from chatbot.tools import llm_for_tools, tools

        print("성공: 도구 모듈이 로드되었습니다.")
        print(f"LLM 모델: {llm_for_tools.model_name}")
        print(f"LLM 온도: {llm_for_tools.temperature}")
        print(f"LLM 최대 토큰: {llm_for_tools.max_tokens}")
        print(f"사용 가능한 도구 개수: {len(tools)}")
        print("도구 목록:")
        for tool in tools:
            print(f"  - {tool.name}")

        return True

    except Exception as e:
        print(f"실패: 도구 모듈 로드 오류 - {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("환경설정 및 도구 모듈 테스트")
    print("=" * 60)

    # 환경설정 테스트
    config_success = test_config_loading()

    # 도구 모듈 테스트
    tools_success = test_tools_loading()

    print("\n" + "=" * 60)
    if config_success and tools_success:
        print("모든 테스트가 성공적으로 완료되었습니다!")
        print("환경설정이 올바르게 적용되었습니다.")
    else:
        print("일부 테스트가 실패했습니다.")
    print("=" * 60)

    return config_success and tools_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)