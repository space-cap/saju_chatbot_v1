# P06: 데이터베이스 스키마 (Database Schema)

## 🗄️ 데이터베이스 아키텍처

사주 챗봇 시스템은 두 가지 데이터베이스를 사용하는 하이브리드 아키텍처를 채택합니다:

```
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│           MySQL                 │    │          ChromaDB               │
│     (관계형 데이터베이스)           │    │       (벡터 데이터베이스)           │
├─────────────────────────────────┤    ├─────────────────────────────────┤
│ • 사용자 세션 데이터                │    │ • 사주 용어 임베딩                 │
│ • 생년월일시 정보 (암호화)           │    │ • 해석 규칙 벡터                  │
│ • 대화 히스토리                    │    │ • 한국어 지식 베이스               │
│ • 계산된 사주 결과                  │    │ • 의미적 유사도 검색               │
└─────────────────────────────────┘    └─────────────────────────────────┘
```

### 설계 원칙
- **데이터 분리**: 구조화된 데이터는 MySQL, 비구조화된 지식은 ChromaDB
- **성능 최적화**: 자주 접근되는 세션 데이터는 MySQL 인덱스 활용
- **확장성**: 벡터 검색과 관계형 쿼리의 각각 최적화
- **보안**: 민감 정보는 암호화하여 MySQL에 저장

## 📊 MySQL 스키마

### 1. users 테이블
사용자 기본 정보를 저장합니다.

```sql
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    preferences JSON DEFAULT NULL COMMENT '사용자 설정 정보',

    INDEX idx_created_at (created_at),
    INDEX idx_last_login (last_login)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='사용자 기본 정보 테이블';
```

### 2. user_sessions 테이블
사용자 세션과 생년월일시 정보를 저장합니다.

```sql
CREATE TABLE user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    birth_datetime DATETIME NULL COMMENT '생년월일시',
    birth_datetime_encrypted TEXT NULL COMMENT '암호화된 생년월일시',
    is_lunar BOOLEAN DEFAULT FALSE COMMENT '음력 여부',
    is_leap_month BOOLEAN DEFAULT FALSE COMMENT '윤달 여부',
    timezone VARCHAR(50) DEFAULT 'Asia/Seoul' COMMENT '시간대',
    birth_location JSON DEFAULT NULL COMMENT '출생지 정보 {city, country, lat, lng}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL 30 MINUTE),

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_last_activity (last_activity),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='사용자 세션 및 생년월일시 정보';
```

### 3. saju_calculations 테이블
계산된 사주 정보를 캐시합니다.

```sql
CREATE TABLE saju_calculations (
    calculation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    birth_datetime DATETIME NOT NULL,
    is_lunar BOOLEAN NOT NULL,

    -- 사주팔자 (천간지지)
    year_ganji CHAR(2) NOT NULL COMMENT '년주 간지',
    month_ganji CHAR(2) NOT NULL COMMENT '월주 간지',
    day_ganji CHAR(2) NOT NULL COMMENT '일주 간지',
    time_ganji CHAR(2) NOT NULL COMMENT '시주 간지',

    -- 음력 정보
    lunar_year INT NULL,
    lunar_month INT NULL,
    lunar_day INT NULL,
    lunar_leap_month BOOLEAN DEFAULT FALSE,

    -- 절기 정보
    season VARCHAR(10) NULL COMMENT '계절',
    jieqi VARCHAR(20) NULL COMMENT '24절기',

    -- 메타데이터
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_version VARCHAR(20) DEFAULT '1.0' COMMENT '계산 알고리즘 버전',

    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    UNIQUE KEY uk_session_birth (session_id, birth_datetime, is_lunar),
    INDEX idx_birth_datetime (birth_datetime),
    INDEX idx_year_ganji (year_ganji),
    INDEX idx_day_ganji (day_ganji)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='계산된 사주 정보 캐시';
```

### 4. saju_analyses 테이블
분석된 사주 정보를 저장합니다.

```sql
CREATE TABLE saju_analyses (
    analysis_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    calculation_id BIGINT NOT NULL,

    -- 일간 정보
    day_gan CHAR(1) NOT NULL COMMENT '일간 (주인공)',
    day_zhi CHAR(1) NOT NULL COMMENT '일지',

    -- 오행 분석
    ohang_wood_count INT DEFAULT 0 COMMENT '목 개수',
    ohang_fire_count INT DEFAULT 0 COMMENT '화 개수',
    ohang_earth_count INT DEFAULT 0 COMMENT '토 개수',
    ohang_metal_count INT DEFAULT 0 COMMENT '금 개수',
    ohang_water_count INT DEFAULT 0 COMMENT '수 개수',
    ohang_dominant VARCHAR(10) NULL COMMENT '우세한 오행',
    ohang_weakest VARCHAR(10) NULL COMMENT '부족한 오행',

    -- 십성 분석
    shipsung_data JSON NULL COMMENT '십성 분석 결과',

    -- 용신/기신
    yongshin VARCHAR(10) NULL COMMENT '용신',
    gishin VARCHAR(10) NULL COMMENT '기신',

    -- 신살
    sinsal_list JSON NULL COMMENT '신살 목록',

    -- 강약 분석
    day_gan_strength ENUM('very_weak', 'weak', 'neutral', 'strong', 'very_strong') NULL,
    overall_balance ENUM('excellent', 'good', 'neutral', 'poor', 'very_poor') NULL,

    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_version VARCHAR(20) DEFAULT '1.0',

    FOREIGN KEY (calculation_id) REFERENCES saju_calculations(calculation_id) ON DELETE CASCADE,
    INDEX idx_day_gan (day_gan),
    INDEX idx_ohang_dominant (ohang_dominant),
    INDEX idx_analyzed_at (analyzed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='사주 분석 결과';
```

### 5. conversation_logs 테이블
대화 기록을 저장합니다.

```sql
CREATE TABLE conversation_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message_order INT NOT NULL COMMENT '메시지 순서',

    role ENUM('user', 'assistant', 'tool') NOT NULL,
    content TEXT NOT NULL,

    -- LLM 관련 정보
    model_name VARCHAR(100) NULL COMMENT '사용된 LLM 모델',
    tool_calls JSON NULL COMMENT '도구 호출 정보',
    tool_call_id VARCHAR(100) NULL COMMENT '도구 호출 ID',

    -- 메타데이터
    tokens_used INT NULL COMMENT '사용된 토큰 수',
    response_time_ms INT NULL COMMENT '응답 시간 (밀리초)',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_order (session_id, message_order),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='대화 기록';
```

### 6. system_metrics 테이블
시스템 메트릭을 저장합니다.

```sql
CREATE TABLE system_metrics (
    metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(20) NULL,

    session_id VARCHAR(255) NULL,
    endpoint VARCHAR(100) NULL,

    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_metric_name (metric_name),
    INDEX idx_recorded_at (recorded_at),
    INDEX idx_session_endpoint (session_id, endpoint)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='시스템 성능 메트릭';
```

## 🧮 ChromaDB 컬렉션

### 1. saju_knowledge 컬렉션
사주 관련 지식을 벡터로 저장합니다.

```python
# ChromaDB 컬렉션 스키마
{
    "collection_name": "saju_knowledge",
    "metadata": {
        "description": "Korean Saju fortune-telling knowledge base",
        "embedding_model": "jhgan/ko-sroberta-multitask",
        "created_at": "2024-01-01T00:00:00Z",
        "version": "1.0"
    },
    "documents": [
        {
            "id": "ganzhi_info_001",
            "content": "갑목(甲木)은 큰 나무의 성질을 가지며...",
            "metadata": {
                "category": "ganzhi",
                "subcategory": "gan",
                "element": "wood",
                "keywords": ["갑목", "甲", "나무", "성격"],
                "source": "traditional_books",
                "importance": 9
            }
        }
    ]
}
```

### 2. interpretation_rules 컬렉션
해석 규칙과 패턴을 저장합니다.

```python
{
    "collection_name": "interpretation_rules",
    "documents": [
        {
            "id": "personality_rule_001",
            "content": "일간이 갑목이고 월지가 인목일 때의 성격 특성...",
            "metadata": {
                "rule_type": "personality",
                "conditions": {
                    "day_gan": "甲",
                    "month_zhi": "寅",
                    "season": "spring"
                },
                "confidence": 0.85,
                "source": "classical_texts"
            }
        }
    ]
}
```

### 3. fortune_patterns 컬렉션
운세 패턴과 예측 규칙을 저장합니다.

```python
{
    "collection_name": "fortune_patterns",
    "documents": [
        {
            "id": "wealth_pattern_001",
            "content": "정재가 월간에 있고 일간이 강할 때의 재물운...",
            "metadata": {
                "pattern_type": "wealth",
                "shipsung_involved": ["정재"],
                "timing": ["monthly"],
                "strength_condition": "strong_day_gan",
                "reliability": 0.78
            }
        }
    ]
}
```

## 🔧 데이터베이스 관리

### MySQL 연결 관리
```python
# database/mysql_manager.py 구조
class MySQLManager:
    def __init__(self):
        self.engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}/{database}",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        """데이터베이스 세션 반환"""
        return self.SessionLocal()

    def save_user_session(self, session_id: str, user_id: str,
                         birth_datetime: datetime, is_lunar: bool,
                         is_leap_month: bool):
        """사용자 세션 저장"""

    def get_user_session(self, session_id: str) -> Dict:
        """사용자 세션 조회"""

    def save_saju_calculation(self, session_id: str, calculation_data: Dict):
        """사주 계산 결과 저장"""
```

### ChromaDB 연결 관리
```python
# database/chroma_manager.py 구조
class ChromaManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=os.getenv("CHROMA_DB_PATH", "./chroma_db")
        )
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )

    def get_or_create_collection(self, name: str):
        """컬렉션 조회 또는 생성"""

    def add_knowledge(self, documents: List[str], metadatas: List[Dict]):
        """지식 추가"""

    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """지식 검색"""
```

## 🔐 보안 및 암호화

### 민감 데이터 암호화
```python
from cryptography.fernet import Fernet
import os

class DataEncryption:
    def __init__(self):
        # 환경변수에서 암호화 키 로드
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # 프로덕션에서는 안전한 키 관리 시스템 사용
        self.cipher = Fernet(key)

    def encrypt_birth_data(self, birth_data: Dict) -> str:
        """생년월일시 암호화"""
        json_data = json.dumps(birth_data, ensure_ascii=False)
        encrypted = self.cipher.encrypt(json_data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_birth_data(self, encrypted_data: str) -> Dict:
        """생년월일시 복호화"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted.decode('utf-8'))
```

### 데이터 마스킹
```sql
-- 개발/테스트 환경에서 실제 생년월일시 마스킹
CREATE VIEW masked_user_sessions AS
SELECT
    session_id,
    user_id,
    CASE
        WHEN birth_datetime IS NOT NULL
        THEN DATE_ADD('1990-01-01', INTERVAL FLOOR(RAND() * 365) DAY)
        ELSE NULL
    END as birth_datetime,
    is_lunar,
    is_leap_month,
    created_at,
    updated_at
FROM user_sessions;
```

## 📈 성능 최적화

### 인덱스 전략
```sql
-- 자주 사용되는 쿼리 패턴에 대한 복합 인덱스
CREATE INDEX idx_session_birth_lunar ON user_sessions(session_id, birth_datetime, is_lunar);
CREATE INDEX idx_ganji_combination ON saju_calculations(year_ganji, month_ganji, day_ganji, time_ganji);
CREATE INDEX idx_ohang_analysis ON saju_analyses(ohang_dominant, ohang_weakest, day_gan_strength);

-- 시간 기반 쿼리 최적화
CREATE INDEX idx_conversation_time_range ON conversation_logs(session_id, created_at DESC);
CREATE INDEX idx_metrics_time_series ON system_metrics(metric_name, recorded_at DESC);
```

### 파티셔닝 전략
```sql
-- 대화 로그 테이블 월별 파티셔닝 (대용량 데이터 처리)
ALTER TABLE conversation_logs
PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    PARTITION p202403 VALUES LESS THAN (202404),
    -- 자동 파티션 관리 스크립트로 확장
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 캐싱 전략
```python
# Redis 캐싱 레이어 추가 (선택사항)
class CachedMySQLManager(MySQLManager):
    def __init__(self):
        super().__init__()
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.cache_ttl = 3600  # 1시간

    def get_user_session(self, session_id: str) -> Dict:
        # 캐시에서 먼저 확인
        cached_data = self.redis_client.get(f"session:{session_id}")
        if cached_data:
            return json.loads(cached_data)

        # 캐시 미스 시 DB에서 조회 후 캐시에 저장
        data = super().get_user_session(session_id)
        if data:
            self.redis_client.setex(
                f"session:{session_id}",
                self.cache_ttl,
                json.dumps(data, default=str)
            )
        return data
```

## 🔄 데이터 마이그레이션

### 스키마 버전 관리
```sql
CREATE TABLE schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rollback_sql TEXT NULL
);

-- 마이그레이션 예시
INSERT INTO schema_migrations (version, description, rollback_sql) VALUES
('1.0.0', 'Initial schema creation', 'DROP DATABASE saju_chatbot;'),
('1.1.0', 'Add user preferences column', 'ALTER TABLE users DROP COLUMN preferences;'),
('1.2.0', 'Add birth location support', 'ALTER TABLE user_sessions DROP COLUMN birth_location;');
```

### 데이터 백업 전략
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)

# MySQL 백업
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    saju_chatbot > "$BACKUP_DIR/saju_chatbot_$DATE.sql"

# ChromaDB 백업 (디렉토리 전체 압축)
tar -czf "$BACKUP_DIR/chromadb_$DATE.tar.gz" ./chroma_db/

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## 📊 모니터링 및 분석

### 데이터베이스 성능 모니터링
```sql
-- 슬로우 쿼리 분석
SELECT
    ROUND(AVG_TIMER_WAIT/1000000000000,6) as avg_exec_time,
    COUNT_STAR as exec_count,
    SUM_TIMER_WAIT/1000000000000 as total_exec_time,
    DIGEST_TEXT as query_pattern
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 10;

-- 인덱스 사용률 분석
SELECT
    object_schema,
    object_name,
    index_name,
    count_read,
    count_insert,
    count_update,
    count_delete
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'saju_chatbot'
ORDER BY count_read DESC;
```

### ChromaDB 사용량 모니터링
```python
def monitor_chromadb_performance():
    """ChromaDB 성능 모니터링"""
    collections_info = []

    for collection_name in ['saju_knowledge', 'interpretation_rules', 'fortune_patterns']:
        collection = chroma_client.get_collection(collection_name)
        count = collection.count()

        collections_info.append({
            'collection': collection_name,
            'document_count': count,
            'last_updated': datetime.now()
        })

    return collections_info
```

---

**다음 문서**: [P07: 테스팅 가이드](p07_testing_guide.md)
**관련 문서**: [P02: 개발환경 설정](p02_setup_guide.md)