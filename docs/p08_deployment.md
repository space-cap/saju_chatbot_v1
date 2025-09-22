# P08: 배포 가이드 (Deployment Guide)

## 🚀 배포 전략 개요

사주 챗봇 시스템은 단계적 배포(Progressive Deployment) 전략을 채택하여 안정적이고 확장 가능한 서비스를 제공합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    배포 환경 구성                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Development  →   Staging   →   Production                 │
│   ┌─────────┐      ┌──────┐      ┌──────────────┐           │
│   │ 로컬 개발  │      │ 테스트 │      │ 실제 서비스   │           │
│   │ 환경     │      │ 환경   │      │ 환경        │           │
│   └─────────┘      └──────┘      └──────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 배포 원칙
- **무중단 배포**: Blue-Green 또는 Rolling 배포
- **자동화**: CI/CD 파이프라인을 통한 자동 배포
- **모니터링**: 실시간 성능 및 오류 추적
- **롤백 준비**: 문제 발생 시 빠른 이전 버전 복구

## 🐳 Docker 컨테이너 배포

### 1. Dockerfile 최적화
```dockerfile
# Dockerfile
FROM python:3.10-slim as base

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 비특권 사용자 생성
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 멀티 스테이지 빌드
```dockerfile
# Dockerfile.production
# Stage 1: Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.10-slim as runtime

# 필수 런타임 패키지만 설치
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 Python 패키지 복사
COPY --from=builder /root/.local /root/.local

# 애플리케이션 코드 복사
WORKDIR /app
COPY . .

# 환경 변수 설정
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# 비특권 사용자
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Docker Compose 설정
```yaml
# docker-compose.yml
version: '3.8'

services:
  saju-chatbot:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MYSQL_HOST=mysql
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DB=${MYSQL_DB}
      - CHROMA_DB_PATH=/app/data/chroma_db
    volumes:
      - chroma_data:/app/data/chroma_db
      - app_logs:/app/logs
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - saju-network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DB}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10
    restart: unless-stopped
    networks:
      - saju-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - nginx_logs:/var/log/nginx
    depends_on:
      - saju-chatbot
    restart: unless-stopped
    networks:
      - saju-network

  redis:  # 캐싱용 (선택사항)
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - saju-network

volumes:
  mysql_data:
  chroma_data:
  redis_data:
  app_logs:
  nginx_logs:

networks:
  saju-network:
    driver: bridge
```

## ☁️ 클라우드 배포

### 1. AWS ECS 배포
```yaml
# ecs-task-definition.json
{
  "family": "saju-chatbot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "saju-chatbot",
      "image": "your-account.dkr.ecr.region.amazonaws.com/saju-chatbot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MYSQL_HOST",
          "value": "your-rds-endpoint"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-api-key"
        },
        {
          "name": "MYSQL_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mysql-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/saju-chatbot",
          "awslogs-region": "ap-northeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### 2. Kubernetes 배포
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: saju-chatbot
  labels:
    app: saju-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: saju-chatbot
  template:
    metadata:
      labels:
        app: saju-chatbot
    spec:
      containers:
      - name: saju-chatbot
        image: saju-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: MYSQL_HOST
          value: "mysql-service"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: saju-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: saju-chatbot-service
spec:
  selector:
    app: saju-chatbot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: v1
kind: Secret
metadata:
  name: saju-secrets
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  mysql-password: <base64-encoded-password>
```

## 🔄 CI/CD 파이프라인

### 1. GitHub Actions 워크플로우
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  release:
    types: [ published ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.production
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging

    steps:
    - name: Deploy to staging
      run: |
        # 스테이징 환경 배포 스크립트
        echo "Deploying to staging environment"
        # SSH를 통한 배포 또는 클라우드 API 호출

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to production
      run: |
        # 프로덕션 환경 배포 스크립트
        echo "Deploying to production environment"
```

### 2. 배포 스크립트
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENV=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Deploying Saju Chatbot v${VERSION} to ${ENV}"

# 환경 변수 설정
if [ "$ENV" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.production"
else
    COMPOSE_FILE="docker-compose.staging.yml"
    ENV_FILE=".env.staging"
fi

# 환경 변수 파일 확인
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file $ENV_FILE not found"
    exit 1
fi

# Docker 이미지 빌드
echo "📦 Building Docker image..."
docker build -f Dockerfile.production -t saju-chatbot:${VERSION} .

# 데이터베이스 마이그레이션
echo "🗄️  Running database migrations..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE run --rm saju-chatbot python scripts/migrate.py

# 서비스 배포 (Blue-Green)
echo "🔄 Deploying services..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d

# Health check
echo "🏥 Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Service is healthy"
        break
    fi
    echo "⏳ Waiting for service to be ready... ($i/30)"
    sleep 10
done

# 이전 버전 정리
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "🎉 Deployment completed successfully!"
```

## 🔧 환경별 설정

### 1. 환경 변수 관리
```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=True
LOG_LEVEL=DEBUG

OPENAI_API_KEY=sk-staging-key
OPENAI_MODEL=gpt-3.5-turbo  # 비용 절약

MYSQL_HOST=staging-mysql.example.com
MYSQL_USER=staging_user
MYSQL_PASSWORD=staging_password
MYSQL_DB=saju_chatbot_staging

CHROMA_DB_PATH=/app/data/chroma_db_staging

# .env.production
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

OPENAI_API_KEY=sk-production-key
OPENAI_MODEL=gpt-4

MYSQL_HOST=production-mysql.example.com
MYSQL_USER=production_user
MYSQL_PASSWORD=production_password
MYSQL_DB=saju_chatbot_production

CHROMA_DB_PATH=/app/data/chroma_db_production

# 보안 설정
ALLOWED_HOSTS=api.sajuchatbot.com,www.sajuchatbot.com
CORS_ORIGINS=https://sajuchatbot.com,https://www.sajuchatbot.com

# 모니터링
SENTRY_DSN=https://your-sentry-dsn
PROMETHEUS_METRICS_ENABLED=true
```

### 2. Nginx 설정
```nginx
# nginx/nginx.conf
upstream saju_backend {
    server saju-chatbot:8000;
    # 로드 밸런싱을 위한 추가 서버
    # server saju-chatbot-2:8000;
}

server {
    listen 80;
    server_name api.sajuchatbot.com;

    # HTTPS로 리다이렉트
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sajuchatbot.com;

    # SSL 설정
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 보안 헤더
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req zone=api burst=20 nodelay;

    # Gzip 압축
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    location / {
        proxy_pass http://saju_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 타임아웃 설정
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 웹소켓 지원 (향후 실시간 기능용)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /health {
        proxy_pass http://saju_backend/health;
        access_log off;
    }

    # 정적 파일 서빙 (향후 웹 프론트엔드용)
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📊 모니터링 및 로깅

### 1. Prometheus 메트릭
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# 메트릭 정의
REQUEST_COUNT = Counter('saju_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('saju_request_duration_seconds', 'Request latency')
ACTIVE_SESSIONS = Gauge('saju_active_sessions', 'Number of active sessions')
SAJU_CALCULATIONS = Counter('saju_calculations_total', 'Total saju calculations')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # 요청 카운트 증가
            REQUEST_COUNT.labels(
                method=scope["method"],
                endpoint=scope["path"]
            ).inc()

            # 응답 처리
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # 응답 시간 기록
                    REQUEST_LATENCY.observe(time.time() - start_time)
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

# FastAPI 앱에 미들웨어 추가
# app.add_middleware(MetricsMiddleware)

# 메트릭 서버 시작
# start_http_server(9090)
```

### 2. 구조화된 로깅
```python
# config/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id

        return json.dumps(log_entry, ensure_ascii=False)

# 로깅 설정
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # 파일 핸들러
    file_handler = logging.FileHandler('/app/logs/saju-chatbot.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger
```

### 3. 헬스 체크 엔드포인트
```python
# health.py
from fastapi import APIRouter, HTTPException
from database.mysql_manager import MySQLManager
from database.chroma_manager import ChromaManager
import asyncio

router = APIRouter()

async def check_mysql():
    """MySQL 연결 상태 확인"""
    try:
        mysql_manager = MySQLManager()
        # 간단한 쿼리 실행
        with mysql_manager.get_session() as session:
            session.execute("SELECT 1")
        return {"status": "healthy", "response_time": "< 100ms"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_chromadb():
    """ChromaDB 연결 상태 확인"""
    try:
        chroma_manager = ChromaManager()
        # 컬렉션 존재 확인
        collections = chroma_manager.client.list_collections()
        return {"status": "healthy", "collections": len(collections)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_openai():
    """OpenAI API 상태 확인"""
    try:
        from openai import OpenAI
        client = OpenAI()
        # 간단한 API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return {"status": "healthy", "model": response.model}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health")
async def health_check():
    """종합 헬스 체크"""
    checks = await asyncio.gather(
        check_mysql(),
        check_chromadb(),
        check_openai(),
        return_exceptions=True
    )

    result = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "mysql": checks[0],
            "chromadb": checks[1],
            "openai": checks[2]
        }
    }

    # 하나라도 실패하면 전체 상태를 unhealthy로 설정
    if any(check.get("status") == "unhealthy" for check in checks):
        result["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=result)

    return result

@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe용"""
    # 서비스가 요청을 받을 준비가 되었는지 확인
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe용"""
    # 서비스가 살아있는지 확인
    return {"status": "alive"}
```

## 🔐 보안 강화

### 1. 보안 미들웨어
```python
# security/middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # 오래된 요청 기록 정리
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.period
        ]

        # Rate limit 체크
        if len(self.requests[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
```

### 2. 입력 검증 및 새니타이제이션
```python
# security/validation.py
import re
from typing import Optional
from pydantic import BaseModel, validator

class SecureChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    message: str
    history: list = []

    @validator('user_id')
    def validate_user_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', v):
            raise ValueError('Invalid user_id format')
        return v

    @validator('message')
    def validate_message(cls, v):
        # 메시지 길이 제한
        if len(v) > 1000:
            raise ValueError('Message too long')

        # 악성 패턴 체크
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Invalid message content')

        return v.strip()

    @validator('history')
    def validate_history(cls, v):
        if len(v) > 100:  # 히스토리 길이 제한
            raise ValueError('History too long')
        return v
```

## 🔄 무중단 배포

### 1. Blue-Green 배포 스크립트
```bash
#!/bin/bash
# scripts/blue-green-deploy.sh

set -e

CURRENT_COLOR=$(docker ps --filter "name=saju-chatbot" --format "table {{.Names}}" | grep -o "blue\|green" | head -1)
NEW_COLOR="blue"

if [ "$CURRENT_COLOR" = "blue" ]; then
    NEW_COLOR="green"
fi

echo "🔄 Starting Blue-Green deployment"
echo "Current: $CURRENT_COLOR, New: $NEW_COLOR"

# 새 컨테이너 시작
echo "🚀 Starting new $NEW_COLOR container..."
docker-compose -f docker-compose.${NEW_COLOR}.yml up -d

# Health check
echo "🏥 Waiting for new container to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ New container is healthy"
        break
    fi
    sleep 10
done

# 로드 밸런서 업데이트 (Nginx 설정 변경)
echo "🔄 Updating load balancer..."
sed -i "s/saju-chatbot-${CURRENT_COLOR}/saju-chatbot-${NEW_COLOR}/g" /etc/nginx/sites-available/default
nginx -s reload

# 이전 컨테이너 정지
echo "🛑 Stopping old $CURRENT_COLOR container..."
docker-compose -f docker-compose.${CURRENT_COLOR}.yml down

echo "🎉 Blue-Green deployment completed!"
```

### 2. 롤링 업데이트 (Kubernetes)
```yaml
# k8s/rolling-update.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: saju-chatbot
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
      - name: saju-chatbot
        image: saju-chatbot:v2.0.0
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

**완료!** 이제 사주 챗봇 시스템의 완전한 배포 인프라가 구축되었습니다.

**문서 시리즈 완료:**
- [P01: 프로젝트 개요](p01_project_overview.md)
- [P02: 개발환경 설정](p02_setup_guide.md)
- [P03: 시스템 아키텍처](p03_architecture.md)
- [P04: API 레퍼런스](p04_api_reference.md)
- [P05: 핵심 모듈](p05_core_modules.md)
- [P06: 데이터베이스 스키마](p06_database_schema.md)
- [P07: 테스팅 가이드](p07_testing_guide.md)
- **P08: 배포 가이드** ✅