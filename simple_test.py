#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 사주 시스템 테스트
Simple Saju System Test
"""

import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모듈 임포트 테스트"""
    print("모듈 임포트 테스트 중...")
    try:
        from core.saju_calculator import SajuCalculator
        from core.saju_analyzer import SajuAnalyzer
        from core.saju_interpreter import SajuInterpreter
        print("성공: 모든 모듈 임포트 완료")
        return True, (SajuCalculator, SajuAnalyzer, SajuInterpreter)
    except Exception as e:
        print(f"실패: 모듈 임포트 오류 - {e}")
        return False, None

def test_calculator(SajuCalculator):
    """사주 계산기 테스트"""
    print("\nSajuCalculator 테스트 중...")
    try:
        calc = SajuCalculator()
        test_birth = datetime(1990, 5, 15, 14, 30)
        result = calc.calculate_saju(test_birth)

        required_keys = ['year_ganji', 'month_ganji', 'day_ganji', 'time_ganji']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"결과에 {key}가 없습니다")

        print("성공: SajuCalculator 정상 작동")
        print(f"  년주: {result['year_ganji']}")
        print(f"  월주: {result['month_ganji']}")
        print(f"  일주: {result['day_ganji']}")
        print(f"  시주: {result['time_ganji']}")
        return True, result
    except Exception as e:
        print(f"실패: SajuCalculator 오류 - {e}")
        return False, None

def test_analyzer(SajuAnalyzer, saju_info):
    """사주 분석기 테스트"""
    print("\nSajuAnalyzer 테스트 중...")
    try:
        analyzer = SajuAnalyzer()
        result = analyzer.analyze_saju(saju_info)

        required_keys = ['ohang_counts', 'day_gan']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"결과에 {key}가 없습니다")

        print("성공: SajuAnalyzer 정상 작동")
        print(f"  일간: {result['day_gan']}")

        ohang_counts = result.get('ohang_counts', {})
        print("  오행 분포:")
        for ohang, count in ohang_counts.items():
            print(f"    {ohang}: {count}개")

        sinsal_results = result.get('sinsal_results', [])
        if sinsal_results:
            print(f"  신살: {', '.join(sinsal_results)}")

        return True, result
    except Exception as e:
        print(f"실패: SajuAnalyzer 오류 - {e}")
        return False, None

def test_interpreter(SajuInterpreter):
    """사주 해석기 테스트"""
    print("\nSajuInterpreter 테스트 중...")
    try:
        interpreter = SajuInterpreter()
        print("성공: SajuInterpreter 초기화 완료")
        return True
    except Exception as e:
        print(f"실패: SajuInterpreter 오류 - {e}")
        return False

def demo_basic_interpretation(analysis):
    """기본 해석 데모"""
    print("\n기본 해석 데모:")
    print("-" * 40)

    day_gan = analysis.get("day_gan", "")
    gan_personality = {
        "甲": "갑목 - 큰 나무처럼 곧고 정직하며 리더십이 있습니다.",
        "乙": "을목 - 꽃이나 풀처럼 부드럽고 유연하며 섬세합니다.",
        "丙": "병화 - 태양처럼 밝고 열정적이며 활동적입니다.",
        "丁": "정화 - 촛불처럼 따뜻하고 세심하며 인정이 많습니다.",
        "戊": "무토 - 산이나 언덕처럼 포용력이 크고 안정적입니다.",
        "己": "기토 - 밭흙처럼 부드럽고 포용력이 있습니다.",
        "庚": "경금 - 쇠처럼 강하고 의지력이 있습니다.",
        "辛": "신금 - 보석처럼 세련되고 품격이 있습니다.",
        "壬": "임수 - 바다나 강물처럼 역동적이고 융통성이 있습니다.",
        "癸": "계수 - 이슬이나 비처럼 섬세하고 지혜롭습니다."
    }

    if day_gan in gan_personality:
        print(f"[성향] {gan_personality[day_gan]}")

    ohang_counts = analysis.get("ohang_counts", {})
    if ohang_counts:
        max_ohang = max(ohang_counts, key=ohang_counts.get)
        ohang_meanings = {
            "木": "성장과 발전의 기운이 강합니다.",
            "火": "열정과 활동의 기운이 강합니다.",
            "土": "안정과 신뢰의 기운이 강합니다.",
            "金": "정의와 의리의 기운이 강합니다.",
            "水": "지혜와 유연성의 기운이 강합니다."
        }
        if max_ohang in ohang_meanings:
            print(f"[특징] {ohang_meanings[max_ohang]}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("사주 시스템 간단 테스트")
    print("=" * 60)

    # 1. 모듈 임포트 테스트
    success, modules = test_imports()
    if not success:
        return False

    SajuCalculator, SajuAnalyzer, SajuInterpreter = modules

    # 2. 계산기 테스트
    success, saju_info = test_calculator(SajuCalculator)
    if not success:
        return False

    # 3. 분석기 테스트
    success, analysis = test_analyzer(SajuAnalyzer, saju_info)
    if not success:
        return False

    # 4. 해석기 테스트
    success = test_interpreter(SajuInterpreter)
    if not success:
        return False

    # 5. 기본 해석 데모
    demo_basic_interpretation(analysis)

    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("콘솔에서 대화형 사주 상담을 시작하려면:")
    print("  python main_simple.py")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n테스트 성공!")
    else:
        print("\n테스트 실패!")
    sys.exit(0 if success else 1)