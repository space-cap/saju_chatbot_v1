# P05: 핵심 모듈 (Core Modules)

## 🔮 모듈 개요

사주 챗봇의 핵심 기능은 세 개의 주요 모듈로 구성되어 있습니다. 각 모듈은 단일 책임 원칙을 따르며, 전통 명리학의 계산 과정을 단계별로 처리합니다.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ SajuCalculator  │───▶│ SajuAnalyzer    │───▶│ SajuInterpreter │
│ 사주 계산        │    │ 오행/십성 분석   │    │ AI 기반 해석     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   천간지지 계산              오행 균형 분석            자연어 해석
   음력 변환                 십성 추출                LLM 기반 상담
   절기 고려                 신살 분석                컨텍스트 관리
```

## 📅 SajuCalculator (사주 계산기)

### 위치
`core/saju_calculator.py`

### 책임
사용자의 생년월일시를 전통 한국 사주명리학의 천간지지 체계로 변환합니다.

### 주요 기능

#### 1. 사주 계산 (`calculate_saju`)
```python
def calculate_saju(self, birth_datetime: datetime) -> Dict[str, Any]:
    """
    생년월일시를 사주(천간지지)로 계산
    
    Args:
        birth_datetime: 생년월일시 (datetime 객체)
        
    Returns:
        {
            'year_ganji': '庚午',     # 년주 (천간지지)
            'month_ganji': '辛巳',    # 월주
            'day_ganji': '甲子',      # 일주
            'time_ganji': '辛未',     # 시주
            'solar_date': datetime,   # 양력 날짜
            'lunar_date': dict,       # 음력 정보
            'season': '春',           # 계절
            'jieqi': '立夏'          # 절기
        }
    """
```

#### 2. 음력 변환 (`get_lunar_date`)
```python
def get_lunar_date(self, solar_date: datetime) -> Dict[str, Any]:
    """
    양력을 음력으로 변환
    
    Args:
        solar_date: 양력 날짜
        
    Returns:
        {
            'lunar_year': 1990,
            'lunar_month': 4,
            'lunar_day': 21,
            'is_leap_month': False,
            'ganzhi_year': '庚午',
            'ganzhi_month': '辛巳',
            'ganzhi_day': '甲子'
        }
    """
```

#### 3. 천간지지 계산 (`calculate_ganzhi`)
```python
def calculate_ganzhi(self, year: int, month: int, day: int, hour: int) -> Tuple[str, str, str, str]:
    """
    년, 월, 일, 시의 천간지지 계산
    
    천간: 甲乙丙丁戊己庚辛壬癸 (10개)
    지지: 子丑寅卯辰巳午未申酉戌亥 (12개)
    
    Returns:
        (년주, 월주, 일주, 시주) 튜플
    """
```

### 핵심 알고리즘

#### 천간지지 계산 공식
```python
# 년주 계산 (60갑자 순환)
year_gan_index = (year - 4) % 10
year_zhi_index = (year - 4) % 12
year_ganji = GAN[year_gan_index] + ZHI[year_zhi_index]

# 월주 계산 (절기 기준)
if self.is_after_jieqi(solar_date, month):
    month_adjust = month
else:
    month_adjust = month - 1
    
# 일주 계산 (기준일로부터 일수 계산)
base_date = datetime(1900, 1, 1)  # 기준일 (甲子일)
days_diff = (solar_date - base_date).days
day_gan_index = days_diff % 10
day_zhi_index = days_diff % 12

# 시주 계산 (일간에 따른 시간별 천간 결정)
time_gan_index = (day_gan_index * 2 + hour_zhi_index) % 10
```

#### 절기 계산
```python
def calculate_jieqi(self, year: int, month: int) -> str:
    """
    24절기 계산
    
    24절기: 입춘(立春), 우수(雨水), 경칩(驚蟄), 춘분(春分),
           청명(清明), 곡우(穀雨), 입하(立夏), 소만(小滿),
           망종(芒種), 하지(夏至), 소서(小暑), 대서(大暑),
           입추(立秋), 처서(處暑), 백로(白露), 추분(秋分),
           한로(寒露), 상강(霜降), 입동(立冬), 소설(小雪),
           대설(大雪), 동지(冬至), 소한(小寒), 대한(大寒)
    """
    # 태양의 황경을 기준으로 정확한 절기 계산
    solar_longitude = self.calculate_solar_longitude(year, month, day)
    return self.get_jieqi_by_longitude(solar_longitude)
```

### 사용 예시
```python
from core.saju_calculator import SajuCalculator
from datetime import datetime

calculator = SajuCalculator()
birth_time = datetime(1990, 5, 15, 14, 30)  # 1990년 5월 15일 14시 30분

result = calculator.calculate_saju(birth_time)
print(f"년주: {result['year_ganji']}")
print(f"월주: {result['month_ganji']}")
print(f"일주: {result['day_ganji']}")
print(f"시주: {result['time_ganji']}")
```

## 🔍 SajuAnalyzer (사주 분석기)

### 위치
`core/saju_analyzer.py`

### 책임
계산된 천간지지를 바탕으로 오행, 십성, 신살 등을 분석합니다.

### 주요 기능

#### 1. 사주 분석 (`analyze_saju`)
```python
def analyze_saju(self, saju_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    사주 데이터를 종합 분석
    
    Args:
        saju_data: SajuCalculator의 출력 결과
        
    Returns:
        {
            'day_gan': '甲',              # 일간 (주인공)
            'ohang_counts': {             # 오행 분포
                '木': 3, '火': 1, '土': 2, '金': 1, '水': 1
            },
            'ohang_strength': {           # 오행 강약
                '木': 'strong', '火': 'weak', '土': 'neutral'
            },
            'shipsung': {                 # 십성 분석
                '比肩': ['甲'], '劫財': ['乙'], '食神': ['丙']
            },
            'yongshin': '火',             # 용신 (필요한 오행)
            'gishin': '水',               # 기신 (도움 되는 오행)
            'sinsal': ['天乙貴人', '桃花']  # 길흉신살
        }
    """
```

#### 2. 오행 분석 (`analyze_ohang`)
```python
def analyze_ohang(self, ganzhi_list: List[str]) -> Dict[str, Any]:
    """
    오행(五行) 분석: 木火土金水
    
    각 천간지지의 오행 속성을 분석하고 균형을 평가
    
    Returns:
        {
            'counts': {'木': 3, '火': 1, '土': 2, '金': 1, '水': 1},
            'percentages': {'木': 37.5, '火': 12.5, ...},
            'dominant': '木',
            'weakest': '火',
            'balance': 'wood_dominant'
        }
    """
```

#### 3. 십성 분석 (`analyze_shipsung`)
```python
def analyze_shipsung(self, day_gan: str, other_gans: List[str]) -> Dict[str, List[str]]:
    """
    십성(十星) 분석: 일간과 다른 천간의 관계
    
    십성:
    - 比肩(비견): 같은 오행, 같은 음양
    - 劫財(겁재): 같은 오행, 다른 음양
    - 食神(식신): 일간이 생하는 오행, 같은 음양
    - 傷官(상관): 일간이 생하는 오행, 다른 음양
    - 偏財(편재): 일간이 극하는 오행, 같은 음양
    - 正財(정재): 일간이 극하는 오행, 다른 음양
    - 偏官(편관): 일간을 극하는 오행, 같은 음양
    - 正官(정관): 일간을 극하는 오행, 다른 음양
    - 偏印(편인): 일간을 생하는 오행, 같은 음양
    - 正印(정인): 일간을 생하는 오행, 다른 음양
    """
```

### 핵심 알고리즘

#### 오행 상생상극
```python
class OhangRelations:
    # 상생: 생성 관계
    GENERATION = {
        '木': '火',  # 목생화
        '火': '土',  # 화생토
        '土': '金',  # 토생금
        '金': '水',  # 금생수
        '水': '木'   # 수생목
    }
    
    # 상극: 극복 관계
    DESTRUCTION = {
        '木': '土',  # 목극토
        '土': '水',  # 토극수
        '水': '火',  # 수극화
        '火': '金',  # 화극금
        '金': '木'   # 금극목
    }
```

#### 십성 관계 매트릭스
```python
def get_shipsung_relation(self, day_gan: str, target_gan: str) -> str:
    """
    일간과 타간의 십성 관계 계산
    """
    day_ohang = self.gan_to_ohang[day_gan]
    target_ohang = self.gan_to_ohang[target_gan]
    
    day_yin_yang = self.get_yin_yang(day_gan)
    target_yin_yang = self.get_yin_yang(target_gan)
    
    # 같은 오행
    if day_ohang == target_ohang:
        return '比肩' if day_yin_yang == target_yin_yang else '劫財'
    
    # 일간이 생하는 오행
    elif self.GENERATION[day_ohang] == target_ohang:
        return '食神' if day_yin_yang == target_yin_yang else '傷官'
    
    # 일간이 극하는 오행
    elif self.DESTRUCTION[day_ohang] == target_ohang:
        return '偏財' if day_yin_yang == target_yin_yang else '正財'
    
    # 일간을 극하는 오행
    elif self.DESTRUCTION[target_ohang] == day_ohang:
        return '偏官' if day_yin_yang == target_yin_yang else '正官'
    
    # 일간을 생하는 오행
    elif self.GENERATION[target_ohang] == day_ohang:
        return '偏印' if day_yin_yang == target_yin_yang else '正印'
```

### 신살 분석
```python
def analyze_sinsal(self, saju_data: Dict) -> List[str]:
    """
    신살(神煞) 분석: 길흉을 나타내는 특수 조합
    
    주요 신살:
    - 천을귀인(天乙貴人): 고귀한 사람의 도움
    - 문창귀인(文昌貴人): 학문과 문예의 재능
    - 역마(驛馬): 이동과 변화
    - 도화(桃花): 인연과 매력
    - 공망(空亡): 허무와 손실
    """
    
    sinsal_list = []
    year_zhi = saju_data['year_ganji'][1]
    day_gan = saju_data['day_ganji'][0]
    
    # 천을귀인 확인
    if self.check_cheonul_gwiin(day_gan, year_zhi):
        sinsal_list.append('天乙貴人')
    
    # 도화 확인
    if self.check_dohwa(year_zhi, day_gan):
        sinsal_list.append('桃花')
    
    return sinsal_list
```

## 🧠 SajuInterpreter (사주 해석기)

### 위치
`core/saju_interpreter.py`

### 책임
LLM(GPT-4)을 활용하여 분석된 사주 데이터를 자연어로 해석합니다.

### 주요 기능

#### 1. 종합 해석 (`interpret_comprehensive`)
```python
def interpret_comprehensive(self, 
                          calculated_saju: Dict, 
                          analyzed_saju: Dict, 
                          question: str = None) -> str:
    """
    사주 데이터를 종합적으로 해석
    
    Args:
        calculated_saju: 계산된 사주 정보
        analyzed_saju: 분석된 사주 정보
        question: 사용자의 구체적 질문 (선택사항)
        
    Returns:
        자연어로 작성된 사주 해석 결과
    """
```

#### 2. 맞춤형 해석 (`interpret_specific`)
```python
def interpret_specific(self, 
                      analyzed_saju: Dict, 
                      aspect: str, 
                      context: str = None) -> str:
    """
    특정 측면에 대한 맞춤형 해석
    
    Args:
        analyzed_saju: 분석된 사주 정보
        aspect: 해석 측면 ('personality', 'fortune', 'career', 'love', 'health')
        context: 추가 컨텍스트
        
    Returns:
        해당 측면에 대한 상세 해석
    """
```

### 해석 템플릿

#### 성격 해석 템플릿
```python
PERSONALITY_TEMPLATE = """
일간 {day_gan}의 기본 성향을 바탕으로 성격을 분석해드리겠습니다.

[기본 성향]
{basic_personality}

[오행 균형에 따른 특성]
{ohang_characteristics}

[십성 분석에 따른 성격]
{shipsung_personality}

[신살의 영향]
{sinsal_effects}

[종합 평가]
{comprehensive_assessment}
"""
```

#### 운세 해석 템플릿
```python
FORTUNE_TEMPLATE = """
{year}년 {name}님의 운세를 분석해드리겠습니다.

[올해의 전체 운세]
{overall_fortune}

[재물운]
{wealth_fortune}

[사업/직장운]
{career_fortune}

[인간관계운]
{relationship_fortune}

[건강운]
{health_fortune}

[주의사항 및 조언]
{advice}
"""
```

### LLM 프롬프트 엔지니어링

#### 시스템 프롬프트
```python
SYSTEM_PROMPT = """
당신은 한국 전통 명리학의 전문가입니다. 사주팔자를 정확하고 친근하게 해석해주는 역할을 합니다.

[해석 원칙]
1. 전통 명리학 이론에 기반한 정확한 해석
2. 현대적 언어로 이해하기 쉬운 설명
3. 긍정적이고 건설적인 조언
4. 과도한 예언이나 단정적 표현 지양
5. 사용자의 질문에 구체적으로 답변

[사용할 데이터]
- 천간지지: {ganzhi_info}
- 오행 분석: {ohang_analysis}
- 십성 분석: {shipsung_analysis}
- 신살 정보: {sinsal_info}

친근하고 전문적인 톤으로 해석해주세요.
"""
```

#### 프롬프트 최적화 기법
```python
class PromptOptimizer:
    def __init__(self):
        self.context_window = 4000  # 토큰 제한
        
    def optimize_prompt(self, saju_data: Dict, question: str) -> str:
        """
        컨텍스트 길이에 맞게 프롬프트 최적화
        """
        # 핵심 정보 추출
        core_info = self.extract_core_info(saju_data)
        
        # 질문 분석하여 관련 정보만 포함
        relevant_info = self.filter_relevant_info(core_info, question)
        
        return self.build_optimized_prompt(relevant_info, question)
```

### 지식 검색 통합
```python
def enhance_with_knowledge(self, interpretation: str, saju_data: Dict) -> str:
    """
    ChromaDB에서 관련 지식을 검색하여 해석을 풍부하게 함
    """
    from database.chroma_manager import ChromaManager
    
    chroma = ChromaManager()
    
    # 관련 키워드 추출
    keywords = self.extract_keywords(saju_data)
    
    # 지식 검색
    knowledge = chroma.search_knowledge(' '.join(keywords), limit=3)
    
    # 해석에 지식 통합
    enhanced_interpretation = self.integrate_knowledge(interpretation, knowledge)
    
    return enhanced_interpretation
```

## 🔧 모듈 간 통합

### 워크플로우 예시
```python
from datetime import datetime
from core.saju_calculator import SajuCalculator
from core.saju_analyzer import SajuAnalyzer
from core.saju_interpreter import SajuInterpreter

def complete_saju_analysis(birth_datetime: datetime, question: str = None) -> str:
    """
    완전한 사주 분석 워크플로우
    """
    # 1단계: 사주 계산
    calculator = SajuCalculator()
    calculated_saju = calculator.calculate_saju(birth_datetime)
    
    # 2단계: 사주 분석
    analyzer = SajuAnalyzer()
    analyzed_saju = analyzer.analyze_saju(calculated_saju)
    
    # 3단계: AI 해석
    interpreter = SajuInterpreter()
    interpretation = interpreter.interpret_comprehensive(
        calculated_saju, analyzed_saju, question
    )
    
    return interpretation

# 사용 예시
birth_time = datetime(1990, 5, 15, 14, 30)
result = complete_saju_analysis(birth_time, "올해 재물운은 어떤가요?")
print(result)
```

### 에러 처리
```python
class SajuCalculationError(Exception):
    """사주 계산 관련 오류"""
    pass

class SajuAnalysisError(Exception):
    """사주 분석 관련 오류"""
    pass

class SajuInterpretationError(Exception):
    """사주 해석 관련 오류"""
    pass

# 각 모듈에서 적절한 예외 처리
try:
    calculated_saju = calculator.calculate_saju(birth_datetime)
except SajuCalculationError as e:
    logger.error(f"사주 계산 오류: {e}")
    return "사주 계산 중 오류가 발생했습니다."
```

## 🧪 테스트 가이드

### 단위 테스트 예시
```python
import pytest
from datetime import datetime
from core.saju_calculator import SajuCalculator

class TestSajuCalculator:
    def setup_method(self):
        self.calculator = SajuCalculator()
    
    def test_calculate_saju_basic(self):
        """기본 사주 계산 테스트"""
        birth_time = datetime(1990, 5, 15, 14, 30)
        result = self.calculator.calculate_saju(birth_time)
        
        assert 'year_ganji' in result
        assert 'month_ganji' in result
        assert 'day_ganji' in result
        assert 'time_ganji' in result
        assert len(result['year_ganji']) == 2
    
    def test_lunar_conversion(self):
        """음력 변환 테스트"""
        solar_date = datetime(1990, 5, 15)
        lunar_result = self.calculator.get_lunar_date(solar_date)
        
        assert 'lunar_year' in lunar_result
        assert 'lunar_month' in lunar_result
        assert 'lunar_day' in lunar_result
        assert isinstance(lunar_result['is_leap_month'], bool)
```

---

**다음 문서**: [P06: 데이터베이스 스키마](p06_database_schema.md)
**관련 문서**: [P07: 테스팅 가이드](p07_testing_guide.md)