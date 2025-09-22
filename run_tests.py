#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 실행 스크립트
Test Runner Script

다양한 테스트 시나리오를 실행할 수 있는 스크립트
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command: list, description: str) -> bool:
    """명령어 실행 및 결과 반환"""
    print(f"\n{'='*60}")
    print(f"실행 중: {description}")
    print(f"명령어: {' '.join(command)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"✅ {description} 성공")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패 (exit code: {e.returncode})")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "-v"],
        "전체 테스트"
    )


def run_api_tests():
    """API 테스트만 실행"""
    return run_command(
        ["python", "-m", "pytest", "tests/test_api.py", "-v"],
        "API 테스트"
    )


def run_model_tests():
    """모델 테스트만 실행"""
    return run_command(
        ["python", "-m", "pytest", "tests/test_models.py", "-v"],
        "모델 테스트"
    )


def run_performance_tests():
    """성능 테스트 실행"""
    return run_command(
        ["python", "-m", "pytest", "tests/test_performance.py", "-v", "-m", "not slow"],
        "성능 테스트 (빠른 테스트만)"
    )


def run_slow_tests():
    """느린 테스트 실행"""
    return run_command(
        ["python", "-m", "pytest", "tests/test_performance.py", "-v", "-m", "slow"],
        "성능 테스트 (느린 테스트)"
    )


def run_with_coverage():
    """커버리지와 함께 테스트 실행"""
    return run_command([
        "python", "-m", "pytest",
        "tests/",
        "--cov=app",
        "--cov=chatbot",
        "--cov=core",
        "--cov=database",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=80",
        "-v"
    ], "커버리지 테스트")


def run_parallel_tests():
    """병렬 테스트 실행 (pytest-xdist 플러그인 필요)"""
    try:
        import xdist  # pytest-xdist 설치 확인
        return run_command(
            ["python", "-m", "pytest", "tests/", "-n", "auto", "-v"],
            "병렬 테스트"
        )
    except ImportError:
        print("❌ pytest-xdist 플러그인이 설치되지 않았습니다.")
        print("설치 명령어: pip install pytest-xdist")
        return False


def run_specific_test(test_path: str):
    """특정 테스트 파일 또는 함수 실행"""
    return run_command(
        ["python", "-m", "pytest", test_path, "-v"],
        f"특정 테스트: {test_path}"
    )


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="사주 챗봇 API 테스트 실행기")

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="모든 테스트 실행"
    )

    parser.add_argument(
        "--api",
        action="store_true",
        help="API 테스트만 실행"
    )

    parser.add_argument(
        "--models",
        action="store_true",
        help="모델 테스트만 실행"
    )

    parser.add_argument(
        "--performance", "-p",
        action="store_true",
        help="성능 테스트 실행 (빠른 테스트)"
    )

    parser.add_argument(
        "--slow",
        action="store_true",
        help="느린 테스트 실행"
    )

    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="커버리지와 함께 테스트 실행"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="병렬 테스트 실행"
    )

    parser.add_argument(
        "--test", "-t",
        type=str,
        help="특정 테스트 파일 또는 함수 실행 (예: tests/test_api.py::TestChatAPI::test_basic_request)"
    )

    args = parser.parse_args()

    # 인자가 없으면 도움말 표시
    if not any(vars(args).values()):
        parser.print_help()
        return

    print("🧪 사주 챗봇 API 테스트 시작")
    print(f"작업 디렉토리: {Path.cwd()}")

    success_count = 0
    total_count = 0

    if args.all:
        total_count += 1
        if run_all_tests():
            success_count += 1

    if args.api:
        total_count += 1
        if run_api_tests():
            success_count += 1

    if args.models:
        total_count += 1
        if run_model_tests():
            success_count += 1

    if args.performance:
        total_count += 1
        if run_performance_tests():
            success_count += 1

    if args.slow:
        total_count += 1
        if run_slow_tests():
            success_count += 1

    if args.coverage:
        total_count += 1
        if run_with_coverage():
            success_count += 1

    if args.parallel:
        total_count += 1
        if run_parallel_tests():
            success_count += 1

    if args.test:
        total_count += 1
        if run_specific_test(args.test):
            success_count += 1

    # 최종 결과
    print(f"\n{'='*60}")
    print("🏁 테스트 실행 완료")
    print(f"성공: {success_count}/{total_count}")

    if success_count == total_count and total_count > 0:
        print("✅ 모든 테스트가 성공했습니다!")
        exit_code = 0
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        exit_code = 1

    print(f"{'='*60}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()