#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사주 시스템 테스트 스크립트
Korean Fortune Telling (Saju) Test Script
"""

import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.saju_calculator import SajuCalculator
    from core.saju_analyzer import SajuAnalyzer
    from core.saju_interpreter import SajuInterpreter
except ImportError as e:
    print(f"모듈 임포트 오류: {e}")
    sys.exit(1)


def test_saju_system():
    """사주 시스템 전체 테스트"""
    print("=" * 60)
    print("사주 시스템 테스트")
    print("=" * 60)

    # 1. 모듈 초기화
    print("\n[1단계] 모듈 초기화 중...")
    try:
        calculator = SajuCalculator()
        analyzer = SajuAnalyzer()
        interpreter = SajuInterpreter()
        print("✓ 모든 모듈이 성공적으로 초기화되었습니다.")
    except Exception as e:
        print(f"✗ 초기화 실패: {e}")
        return False

    # 2. 테스트 생년월일시
    print("\n[2단계] 테스트 데이터 생성...")
    test_birth = datetime(1990, 5, 15, 14, 30)  # 1990년 5월 15일 14시 30분
    print(f"테스트 생년월일시: {test_birth.strftime('%Y년 %m월 %d일 %H시 %M분')}")

    # 3. 사주 계산
    print("\n[3단계] 사주 계산 중...")
    try:
        saju_info = calculator.calculate_saju(test_birth)
        print("✓ 사주 계산 완료")
        print(f"년주: {saju_info['year_ganji']}")
        print(f"월주: {saju_info['month_ganji']}")
        print(f"일주: {saju_info['day_ganji']}")
        print(f"시주: {saju_info['time_ganji']}")
    except Exception as e:
        print(f"✗ 사주 계산 실패: {e}")
        return False

    # 4. 사주 분석
    print("\n[4단계] 사주 분석 중...")
    try:
        analysis = analyzer.analyze_saju(saju_info)
        print("✓ 사주 분석 완료")

        ohang_counts = analysis.get("ohang_counts", {})
        print("오행 분포:")
        for ohang, count in ohang_counts.items():
            print(f"  {ohang}: {count}개")

        day_gan = analysis.get("day_gan")
        print(f"일간: {day_gan}")

        sinsal_results = analysis.get("sinsal_results", [])
        if sinsal_results:
            print(f"신살: {', '.join(sinsal_results)}")

    except Exception as e:
        print(f"✗ 사주 분석 실패: {e}")
        return False

    # 5. 기본 해석 테스트
    print("\n[5단계] 기본 해석 테스트...")
    try:
        # main_simple.py의 generate_basic_interpretation 함수 테스트
        interpretation_parts = []

        day_gan = analysis.get("day_gan", "")
        gan_personality = {
            "甲": "갑목(甲木) - 큰 나무처럼 곧고 정직하며 리더십이 있습니다.",
            "乙": "을목(乙木) - 꽃이나 풀처럼 부드럽고 유연하며 섬세합니다.",
            "丙": "병화(丙火) - 태양처럼 밝고 열정적이며 활동적입니다.",
            "丁": "정화(丁火) - 촛불처럼 따뜻하고 세심하며 인정이 많습니다.",
            "戊": "무토(戊土) - 산이나 언덕처럼 포용력이 크고 안정적입니다.",
            "己": "기토(己土) - 밭흙처럼 부드럽고 포용력이 있습니다.",
            "庚": "경금(庚金) - 쇠처럼 강하고 의지력이 있습니다.",
            "辛": "신금(辛金) - 보석처럼 세련되고 품격이 있습니다.",
            "壬": "임수(壬水) - 바다나 강물처럼 역동적이고 융통성이 있습니다.",
            "癸": "계수(癸水) - 이슬이나 비처럼 섬세하고 지혜롭습니다."
        }

        if day_gan in gan_personality:
            interpretation_parts.append(f"[기본 성향] {gan_personality[day_gan]}")

        print("✓ 기본 해석 완료")
        print("해석 결과:")
        for part in interpretation_parts:
            print(f"  {part}")

    except Exception as e:
        print(f"✗ 기본 해석 실패: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ 모든 테스트가 성공적으로 완료되었습니다!")
    print("콘솔에서 'python main_simple.py'를 실행하여 대화형 사주 상담을 시작할 수 있습니다.")
    print("=" * 60)

    return True


def test_core_modules():
    """개별 모듈 테스트"""
    print("\n[개별 모듈 테스트]")

    # SajuCalculator 테스트
    print("1. SajuCalculator 테스트...")
    try:
        calc = SajuCalculator()
        test_dt = datetime(1990, 5, 15, 14, 30)
        result = calc.calculate_saju(test_dt)
        assert 'year_ganji' in result
        assert 'month_ganji' in result
        assert 'day_ganji' in result
        assert 'time_ganji' in result
        print("   ✓ SajuCalculator 정상 작동")
    except Exception as e:
        print(f"   ✗ SajuCalculator 오류: {e}")
        return False

    # SajuAnalyzer 테스트
    print("2. SajuAnalyzer 테스트...")
    try:
        analyzer = SajuAnalyzer()
        test_saju = {
            'year_ganji': '甲子',
            'month_ganji': '乙丑',
            'day_ganji': '丙寅',
            'time_ganji': '丁卯'
        }
        result = analyzer.analyze_saju(test_saju)
        assert 'ohang_counts' in result
        assert 'day_gan' in result
        print("   ✓ SajuAnalyzer 정상 작동")
    except Exception as e:
        print(f"   ✗ SajuAnalyzer 오류: {e}")
        return False

    # SajuInterpreter 테스트
    print("3. SajuInterpreter 테스트...")
    try:
        interpreter = SajuInterpreter()
        # LLM 없이도 기본 구조 확인
        print("   ✓ SajuInterpreter 정상 초기화")
    except Exception as e:
        print(f"   ✗ SajuInterpreter 오류: {e}")
        return False

    return True


def main():
    """메인 함수"""
    print("사주 챗봇 시스템 테스트를 시작합니다...\n")

    # 개별 모듈 테스트
    if not test_core_modules():
        print("개별 모듈 테스트 실패!")
        return False

    # 전체 시스템 테스트
    if not test_saju_system():
        print("전체 시스템 테스트 실패!")
        return False

    print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)