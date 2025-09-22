# P02: 개발환경 설정 가이드 (Development Setup Guide)

## 🛠️ 시스템 요구사항

### 최소 요구사항
- **운영체제**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 이상 (권장: 3.10+)
- **메모리**: 최소 4GB RAM (권장: 8GB+)
- **저장공간**: 최소 2GB 여유 공간
- **네트워크**: 인터넷 연결 (OpenAI API, 패키지 다운로드용)

### 권장 개발 환경
- **IDE**: VS Code, PyCharm Professional
- **터미널**: PowerShell (Windows), Terminal (macOS/Linux)
- **Git**: 최신 버전
- **Docker**: 선택사항 (컨테이너 배포용)

## 📦 1단계: Python 환경 설정

### Python 설치 확인
```bash
python --version
# 또는
python3 --version
```

### 가상환경 생성 및 활성화
```bash
# 프로젝트 디렉토리로 이동
cd saju_chatbot_v1

# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

### 패키지 의존성 설치
```bash
# 기본 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 개발용 추가 패키지 (선택사항)
pip install black flake8 mypy pre-commit
```

## 🔑 2단계: 환경변수 설정

### .env 파일 생성
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```bash
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# MySQL 데이터베이스 설정
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=saju_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=saju_chatbot

# ChromaDB 설정
CHROMA_DB_PATH=./chroma_db

# 애플리케이션 설정
DEBUG=True
LOG_LEVEL=INFO
```

### 환경변수 설명

| 변수명 | 필수 | 설명 | 기본값 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | ✅ | OpenAI API 키 | - |
| `OPENAI_MODEL` | ❌ | 사용할 GPT 모델 | gpt-4 |
| `OPENAI_TEMPERATURE` | ❌ | 응답 창의성 수준 (0.0-1.0) | 0.7 |
| `MYSQL_HOST` | ✅ | MySQL 서버 주소 | localhost |
| `MYSQL_PORT` | ❌ | MySQL 포트 | 3306 |
| `MYSQL_USER` | ✅ | MySQL 사용자명 | - |
| `MYSQL_PASSWORD` | ✅ | MySQL 비밀번호 | - |
| `MYSQL_DB` | ✅ | 데이터베이스 이름 | saju_chatbot |
| `CHROMA_DB_PATH` | ❌ | ChromaDB 저장 경로 | ./chroma_db |
| `DEBUG` | ❌ | 디버그 모드 | False |
| `LOG_LEVEL` | ❌ | 로그 레벨 | INFO |

## 🗄️ 3단계: 데이터베이스 설정

### MySQL 설치 및 설정

#### MySQL 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# macOS (Homebrew)
brew install mysql

# Windows: MySQL Installer 다운로드
# https://dev.mysql.com/downloads/installer/
```

#### 데이터베이스 및 사용자 생성
```sql
-- MySQL 접속
mysql -u root -p

-- 데이터베이스 생성
CREATE DATABASE saju_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 및 권한 부여
CREATE USER 'saju_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON saju_chatbot.* TO 'saju_user'@'localhost';
FLUSH PRIVILEGES;

-- 연결 테스트
USE saju_chatbot;
SHOW TABLES;
```

### ChromaDB 초기화
ChromaDB는 첫 실행 시 자동으로 초기화되지만, 수동으로 설정할 수도 있습니다:

```python
# 초기화 스크립트 실행 (선택사항)
python -c "
from database.chroma_manager import ChromaManager
manager = ChromaManager()
manager.initialize_collection()
print('ChromaDB 초기화 완료')
"
```

## 🔧 4단계: IDE 설정

### VS Code 설정
`.vscode/settings.json` 파일 생성:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".venv": true,
        "chroma_db": true
    },
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### 권장 VS Code 확장
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "ms-python.mypy-type-checker",
        "ms-toolsai.jupyter",
        "redhat.vscode-yaml",
        "ms-vscode.vscode-json"
    ]
}
```

## ✅ 5단계: 설치 검증

### 시스템 테스트 실행
```bash
# 핵심 모듈 테스트
python test_saju.py

# pytest 테스트 스위트 실행
python run_tests.py

# 또는 직접 pytest 실행
pytest tests/ -v
```

### FastAPI 서버 실행 테스트
```bash
# 개발 서버 시작
python app.py

# 브라우저에서 확인
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### API 엔드포인트 테스트
```bash
# curl을 사용한 API 테스트
curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "session_id": "test_session",
       "message": "안녕하세요",
       "history": []
     }'
```

## 🐳 6단계: Docker 설정 (선택사항)

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MYSQL_HOST=mysql
      - MYSQL_USER=saju_user
      - MYSQL_PASSWORD=saju_password
      - MYSQL_DB=saju_chatbot
    depends_on:
      - mysql
    volumes:
      - ./chroma_db:/app/chroma_db

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=saju_chatbot
      - MYSQL_USER=saju_user
      - MYSQL_PASSWORD=saju_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

## 🔍 7단계: 문제 해결

### 자주 발생하는 문제들

#### 1. OpenAI API 키 오류
```
openai.error.AuthenticationError: Incorrect API key provided
```
**해결방법**: `.env` 파일의 `OPENAI_API_KEY` 확인 및 유효성 검증

#### 2. MySQL 연결 오류
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```
**해결방법**:
- MySQL 서비스 실행 상태 확인
- 방화벽 설정 확인
- `.env` 파일의 MySQL 설정 확인

#### 3. 가상환경 활성화 문제 (Windows)
```
cannot be loaded because running scripts is disabled on this system
```
**해결방법**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. 패키지 설치 오류
```
error: Microsoft Visual C++ 14.0 is required
```
**해결방법**:
- Windows: Visual Studio Build Tools 설치
- 또는 미리 컴파일된 wheel 패키지 사용

### 로그 확인
```bash
# 애플리케이션 로그 확인
tail -f logs/app.log

# MySQL 로그 확인 (Ubuntu)
sudo tail -f /var/log/mysql/error.log

# 시스템 로그 확인
journalctl -u mysql.service -f
```

## 📊 8단계: 성능 최적화 설정

### Python 최적화
```bash
# 최적화된 Python 실행
export PYTHONOPTIMIZE=1
python -O app.py
```

### 메모리 설정
```bash
# .env 파일에 추가
WORKERS=4
WORKER_MEMORY_LIMIT=512M
```

### 캐시 설정
```python
# Redis 캐시 (선택사항)
pip install redis

# .env 파일에 추가
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

## 🚀 9단계: 개발 워크플로우

### Git 훅 설정
```bash
# pre-commit 설치 및 설정
pip install pre-commit
pre-commit install

# .pre-commit-config.yaml 생성
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3.10
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
EOF
```

### 개발 스크립트
```bash
# 개발 시작 스크립트 (scripts/dev-start.sh)
#!/bin/bash
source .venv/bin/activate
export FLASK_ENV=development
python app.py

# 테스트 실행 스크립트 (scripts/test.sh)
#!/bin/bash
source .venv/bin/activate
python test_saju.py && pytest tests/ -v --cov=.
```

---

**다음 단계**: [P03: 시스템 아키텍처](p03_architecture.md)

**문제가 있나요?**
- GitHub Issues: [프로젝트 이슈 트래커]
- 문서 개선 제안: docs/ 폴더에 PR 제출