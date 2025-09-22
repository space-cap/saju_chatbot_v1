#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사주 챗봇 콘솔 인터페이스 (간단 버전)
Korean Fortune Telling (Saju) Console Interface (Simple Version)
"""

import sys
import os
from datetime import datetime
from typing import Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.saju_calculator import SajuCalculator
    from core.saju_analyzer import SajuAnalyzer
    from core.saju_interpreter import SajuInterpreter
except ImportError as e:
    print(f"모듈 임포트 오류: {e}")
    sys.exit(1)


class SajuConsole:
    """콘솔 기반 사주 상담 시스템"""

    def __init__(self):
        print("사주 시스템을 초기화하고 있습니다...")
        try:
            self.calculator = SajuCalculator()
            self.analyzer = SajuAnalyzer()
            self.interpreter = SajuInterpreter()
            print("초기화 완료!")
        except Exception as e:
            print(f"초기화 오류: {e}")
            raise

    def print_welcome(self):
        """환영 메시지 출력"""
        print("=" * 60)
        print("한국 전통 사주팔자 상담 시스템")
        print("Korean Traditional Fortune Telling (Saju) System")
        print("=" * 60)
        print()
        print("안녕하세요! 사주팔자 상담을 시작합니다.")
        print("정확한 생년월일시를 입력해주시면 사주를 풀이해드립니다.")
        print()

    def get_birth_info(self) -> Optional[datetime]:
        """사용자로부터 생년월일시 입력받기"""
        print("[생년월일시 입력]")
        print("-" * 30)

        while True:
            try:
                # 연도 입력
                year_input = input("태어난 년도 (예: 1990): ").strip()
                if not year_input:
                    print("[오류] 년도를 입력해주세요.")
                    continue
                year = int(year_input)

                if year < 1900 or year > 2100:
                    print("[오류] 1900년 ~ 2100년 사이의 년도를 입력해주세요.")
                    continue

                # 월 입력
                month_input = input("태어난 월 (1-12): ").strip()
                if not month_input:
                    print("[오류] 월을 입력해주세요.")
                    continue
                month = int(month_input)

                if month < 1 or month > 12:
                    print("[오류] 1~12 사이의 월을 입력해주세요.")
                    continue

                # 일 입력
                day_input = input("태어난 일 (1-31): ").strip()
                if not day_input:
                    print("[오류] 일을 입력해주세요.")
                    continue
                day = int(day_input)

                if day < 1 or day > 31:
                    print("[오류] 1~31 사이의 일을 입력해주세요.")
                    continue

                # 시간 입력
                hour_input = input("태어난 시간 (0-23, 모르면 12 입력): ").strip()
                if not hour_input:
                    hour = 12  # 기본값
                    print("[알림] 시간을 모르시므로 정오(12시)로 설정합니다.")
                else:
                    hour = int(hour_input)
                    if hour < 0 or hour > 23:
                        print("[오류] 0~23 사이의 시간을 입력해주세요.")
                        continue

                # 분 입력 (선택사항)
                minute_input = input("태어난 분 (0-59, 선택사항, 엔터시 0분): ").strip()
                minute = 0
                if minute_input:
                    minute = int(minute_input)
                    if minute < 0 or minute > 59:
                        print("[오류] 0~59 사이의 분을 입력해주세요.")
                        continue

                # datetime 객체 생성
                birth_datetime = datetime(year, month, day, hour, minute)

                # 확인
                print()
                print("[입력하신 정보 확인]")
                print(f"   생년월일시: {birth_datetime.strftime('%Y년 %m월 %d일 %H시 %M분')}")

                confirm = input("맞습니까? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', 'ㅇ', '네', '맞습니다']:
                    return birth_datetime
                elif confirm in ['n', 'no', 'ㄴ', '아니요', '다시']:
                    print("[안내] 다시 입력해주세요.\n")
                    continue
                else:
                    print("[안내] y 또는 n으로 답해주세요.")
                    continue

            except ValueError as e:
                print(f"[오류] 잘못된 입력입니다. 숫자로 입력해주세요. ({e})")
                continue
            except Exception as e:
                print(f"[오류] 입력 오류: {e}")
                continue

    def display_saju_info(self, saju_info: dict):
        """사주팔자 정보 표시"""
        print("\n" + "=" * 60)
        print("사주팔자 (四柱八字)")
        print("=" * 60)

        print(f"년주(年柱): {saju_info['year_ganji']} (연간: {saju_info['year_ganji'][0]}, 연지: {saju_info['year_ganji'][1]})")
        print(f"월주(月柱): {saju_info['month_ganji']} (월간: {saju_info['month_ganji'][0]}, 월지: {saju_info['month_ganji'][1]})")
        print(f"일주(日柱): {saju_info['day_ganji']} (일간: {saju_info['day_ganji'][0]}, 일지: {saju_info['day_ganji'][1]})")
        print(f"시주(時柱): {saju_info['time_ganji']} (시간: {saju_info['time_ganji'][0]}, 시지: {saju_info['time_ganji'][1]})")
        print()
        print("[중요] 일간(日干)은 당신 자신을 나타내는 핵심 요소입니다.")
        print(f"당신의 일간: {saju_info['day_ganji'][0]}")

    def display_analysis(self, analysis: dict):
        """사주 분석 결과 표시"""
        print("\n" + "=" * 60)
        print("사주 분석 결과")
        print("=" * 60)

        # 오행 분석
        print("오행(五行) 분포:")
        ohang_mapping = {
            "木": "목(木) - 나무",
            "火": "화(火) - 불",
            "土": "토(土) - 흙",
            "金": "금(金) - 쇠",
            "水": "수(水) - 물"
        }

        ohang_counts = analysis.get("ohang_counts", {})
        for ohang, count in ohang_counts.items():
            print(f"   {ohang_mapping.get(ohang, ohang)}: {count}개")

        if not ohang_counts:
            print("   (오행 정보를 계산 중입니다...)")

        # 십성 분석
        print("\n십성(十星) 분포:")
        sipsung_results = analysis.get("sipsung_results", {})
        for position, sipsung in sipsung_results.items():
            if sipsung and sipsung != "알 수 없음":
                position_kr = position.replace("_", " ").replace("천간", "(천간)").replace("지지", "(지지)")
                print(f"   {position_kr}: {sipsung}")

        # 신살 분석
        sinsal_results = analysis.get("sinsal_results", [])
        if sinsal_results:
            print("\n신살(神殺):")
            for sinsal in sinsal_results:
                print(f"   {sinsal}")

        # 일간 정보
        day_gan = analysis.get("day_gan")
        if day_gan:
            print(f"\n일간: {day_gan}")

    def get_user_question(self) -> str:
        """사용자의 추가 질문 받기"""
        print("\n" + "=" * 60)
        print("추가 질문이 있으시면 입력해주세요")
        print("=" * 60)
        print("예시: 올해 운세는?, 직업운은?, 연애운은?, 건강운은? 등")
        print("(질문이 없으시면 엔터를 눌러주세요)")

        question = input("질문: ").strip()
        return question if question else "전반적인 운세를 알려주세요"

    def display_interpretation(self, interpretation: str):
        """사주 해석 결과 표시"""
        print("\n" + "=" * 80)
        print("사주 해석")
        print("=" * 80)
        print(interpretation)
        print("=" * 80)

    def ask_continue(self) -> bool:
        """계속할지 묻기"""
        print("\n다른 사주를 보시겠습니까? (y/n): ", end="")
        response = input().strip().lower()
        return response in ['y', 'yes', 'ㅇ', '네', '계속']

    def run(self):
        """메인 실행 함수"""
        self.print_welcome()

        while True:
            try:
                # 1. 생년월일시 입력받기
                birth_datetime = self.get_birth_info()
                if not birth_datetime:
                    print("[알림] 생년월일시 입력이 취소되었습니다.")
                    break

                print("\n[처리중] 사주를 계산하고 있습니다...")

                # 2. 사주 계산
                saju_info = self.calculator.calculate_saju(birth_datetime)

                # 3. 사주 정보 표시
                self.display_saju_info(saju_info)

                # 4. 사주 분석
                print("\n[처리중] 사주를 분석하고 있습니다...")
                analysis = self.analyzer.analyze_saju(saju_info)

                # 5. 분석 결과 표시
                self.display_analysis(analysis)

                # 6. 사용자 질문 받기
                user_question = self.get_user_question()

                # 7. 사주 해석 (LLM 없이 기본 해석)
                print("\n[처리중] 사주를 해석하고 있습니다...")
                interpretation = self.generate_basic_interpretation(saju_info, analysis, user_question)

                # 8. 해석 결과 표시
                self.display_interpretation(interpretation)

                # 9. 계속할지 묻기
                if not self.ask_continue():
                    break

                print("\n" + "=" * 20 + " 새로운 상담 " + "=" * 20)

            except KeyboardInterrupt:
                print("\n\n[종료] 사주 상담을 종료합니다.")
                break
            except Exception as e:
                print(f"\n[오류] 오류가 발생했습니다: {e}")
                print("[안내] 다시 시도해주세요.\n")
                continue

        print("\n사주 상담을 이용해주셔서 감사합니다!")
        print("좋은 하루 되세요!")

    def generate_basic_interpretation(self, saju_info: dict, analysis: dict, user_question: str) -> str:
        """LLM 없이 기본적인 사주 해석 생성"""
        interpretation_parts = []

        # 일간 기반 기본 성격 해석
        day_gan = analysis.get("day_gan", "")
        gan_personality = {
            "甲": "갑목(甲木) - 큰 나무처럼 곧고 정직하며 리더십이 있습니다. 진취적이고 추진력이 강한 성향입니다.",
            "乙": "을목(乙木) - 꽃이나 풀처럼 부드럽고 유연하며 섬세합니다. 배려심이 깊고 적응력이 좋습니다.",
            "丙": "병화(丙火) - 태양처럼 밝고 열정적이며 활동적입니다. 솔직하고 명랑한 성향을 가집니다.",
            "丁": "정화(丁火) - 촛불처럼 따뜻하고 세심하며 인정이 많습니다. 예술적 감성과 직관력이 뛰어납니다.",
            "戊": "무토(戊土) - 산이나 언덕처럼 포용력이 크고 안정적입니다. 책임감이 강하고 신뢰받는 성향입니다.",
            "己": "기토(己土) - 밭흙처럼 부드럽고 포용력이 있습니다. 실용적이고 현실적인 판단력을 가집니다.",
            "庚": "경금(庚金) - 쇠처럼 강하고 의지력이 있습니다. 정의감이 강하고 원칙을 중시하는 성향입니다.",
            "辛": "신금(辛金) - 보석처럼 세련되고 품격이 있습니다. 예리한 판단력과 미적 감각이 뛰어납니다.",
            "壬": "임수(壬水) - 바다나 강물처럼 역동적이고 융통성이 있습니다. 지혜롭고 포용력이 큰 성향입니다.",
            "癸": "계수(癸水) - 이슬이나 비처럼 섬세하고 지혜롭습니다. 직감력이 뛰어나고 신비로운 매력을 가집니다."
        }

        if day_gan in gan_personality:
            interpretation_parts.append(f"[기본 성향]\n{gan_personality[day_gan]}")

        # 오행 균형 해석
        ohang_counts = analysis.get("ohang_counts", {})
        if ohang_counts:
            max_ohang = max(ohang_counts, key=ohang_counts.get)
            min_ohang = min(ohang_counts, key=ohang_counts.get) if len(ohang_counts) > 1 else None

            ohang_meanings = {
                "木": "성장과 발전의 기운이 강합니다. 새로운 시작과 변화에 적극적입니다.",
                "火": "열정과 활동의 기운이 강합니다. 밝고 적극적인 에너지를 가지고 있습니다.",
                "土": "안정과 신뢰의 기운이 강합니다. 든든하고 포용력 있는 성향을 보입니다.",
                "金": "정의와 의리의 기운이 강합니다. 원칙적이고 완성도 높은 일을 선호합니다.",
                "水": "지혜와 유연성의 기운이 강합니다. 적응력이 뛰어나고 깊이 있는 사고를 합니다."
            }

            if max_ohang in ohang_meanings:
                interpretation_parts.append(f"[오행 특징]\n{ohang_meanings[max_ohang]}")

            if min_ohang and ohang_counts[min_ohang] == 0:
                missing_advice = {
                    "木": "목(木) 기운을 보완하면 좋습니다. 새로운 도전이나 학습을 통해 성장 동력을 얻으세요.",
                    "火": "화(火) 기운을 보완하면 좋습니다. 적극적인 활동이나 사교 활동으로 에너지를 충전하세요.",
                    "土": "토(土) 기운을 보완하면 좋습니다. 안정감을 주는 환경이나 관계를 중시하세요.",
                    "金": "금(金) 기운을 보완하면 좋습니다. 체계적이고 완성도 높은 일에 집중하세요.",
                    "水": "수(水) 기운을 보완하면 좋습니다. 학습이나 내적 성찰을 통해 지혜를 쌓으세요."
                }
                if min_ohang in missing_advice:
                    interpretation_parts.append(f"[개선 방향]\n{missing_advice[min_ohang]}")

        # 신살 해석
        sinsal_results = analysis.get("sinsal_results", [])
        if "도화살" in sinsal_results:
            interpretation_parts.append("[도화살] 이성에게 인기가 많고 매력적인 기운을 가지고 있습니다. 대인관계에서 장점이 될 수 있습니다.")

        # 사용자 질문에 대한 기본 답변
        if "직업" in user_question or "일" in user_question or "career" in user_question.lower():
            interpretation_parts.append("[직업운] 당신의 일간과 오행 특성을 고려할 때, 꾸준한 노력과 성실함으로 좋은 성과를 얻을 수 있습니다.")
        elif "연애" in user_question or "사랑" in user_question or "결혼" in user_question:
            interpretation_parts.append("[연애운] 진실한 마음으로 상대방을 대하면 좋은 인연을 만날 수 있습니다. 자신의 매력을 자연스럽게 드러내세요.")
        elif "건강" in user_question:
            interpretation_parts.append("[건강운] 규칙적인 생활과 적절한 운동으로 건강을 유지하세요. 스트레스 관리에 특히 신경 쓰시기 바랍니다.")
        elif "재물" in user_question or "돈" in user_question or "투자" in user_question:
            interpretation_parts.append("[재물운] 성실한 노력과 계획적인 관리로 재물을 축적할 수 있습니다. 무리한 투자보다는 안정적인 방법을 선택하세요.")

        # 전반적인 조언
        interpretation_parts.append("[종합] 전체적으로 당신은 고유한 장점과 잠재력을 가지고 있습니다. 자신감을 가지고 꾸준히 노력하시면 원하는 목표를 달성할 수 있을 것입니다.")

        return "\n\n".join(interpretation_parts)


def main():
    """메인 함수"""
    try:
        console = SajuConsole()
        console.run()
    except Exception as e:
        print(f"[오류] 프로그램 실행 중 오류가 발생했습니다: {e}")
        print("[안내] 개발자에게 문의해주세요.")


if __name__ == "__main__":
    main()