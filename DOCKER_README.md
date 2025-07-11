# 🐳 골프 스윙 분석기 Docker 배포 가이드

Docker를 사용하여 골프 스윙 분석기를 쉽게 배포할 수 있습니다.

## 🚀 빠른 시작

### 1. Docker 설치 확인
```bash
docker --version
docker-compose --version
```

### 2. 프로젝트 클론
```bash
git clone <repository-url>
cd motion
```

### 3. 배포 스크립트 실행
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. 브라우저에서 접속
- **OpenCV 버전 (권장)**: http://localhost:5000
- **MediaPipe 버전**: http://localhost:5001
- **Nginx 프록시**: http://localhost:80

## 📋 수동 배포 방법

### OpenCV 버전 (권장)
```bash
# 이미지 빌드
docker build -f Dockerfile.simple -t golf-analyzer-simple .

# 컨테이너 실행
docker run -d -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  --name golf-analyzer-simple \
  golf-analyzer-simple
```

### MediaPipe 버전
```bash
# 이미지 빌드
docker build -f Dockerfile -t golf-analyzer-advanced .

# 컨테이너 실행
docker run -d -p 5001:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  --name golf-analyzer-advanced \
  golf-analyzer-advanced
```

### Docker Compose 사용
```bash
# 모든 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d golf-analyzer-simple
```

## 🔧 관리 명령어

### 컨테이너 관리
```bash
# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f golf-analyzer-simple

# 컨테이너 재시작
docker-compose restart

# 컨테이너 중지
docker-compose down

# 이미지 재빌드
docker-compose build --no-cache
```

### 볼륨 관리
```bash
# 업로드 파일 확인
ls -la uploads/

# 결과 파일 확인
ls -la results/

# 볼륨 정리
docker-compose down -v
```

## 🌐 프로덕션 배포

### 1. 환경 변수 설정
```bash
# .env 파일 생성
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your_super_secret_key_here
UPLOAD_MAX_SIZE=100M
EOF
```

### 2. Nginx 설정 (선택사항)
```bash
# Nginx 설정 파일 수정
sudo nano nginx.conf

# SSL 인증서 추가 (권장)
sudo certbot --nginx -d your-domain.com
```

### 3. 방화벽 설정
```bash
# 포트 열기
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
```

## 📊 모니터링

### 로그 확인
```bash
# 실시간 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f golf-analyzer-simple

# 로그 파일 저장
docker-compose logs > app.log
```

### 리소스 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
docker system df
```

## 🔍 문제 해결

### 포트 충돌
```bash
# 포트 확인
netstat -tulpn | grep :5000

# 다른 포트 사용
docker run -d -p 5002:5000 golf-analyzer-simple
```

### 메모리 부족
```bash
# Docker 메모리 제한 설정
docker run -d -p 5000:5000 \
  --memory=2g \
  --memory-swap=4g \
  golf-analyzer-simple
```

### 빌드 실패
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 특정 단계부터 재빌드
docker build --target python -f Dockerfile.simple .
```

## 🚀 클라우드 배포

### AWS EC2
```bash
# EC2 인스턴스에 Docker 설치
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 애플리케이션 배포
git clone <repository-url>
cd motion
./deploy.sh
```

### Google Cloud Run
```bash
# Cloud Run 배포
gcloud run deploy golf-analyzer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances
```bash
# Azure CLI로 배포
az container create \
  --resource-group myResourceGroup \
  --name golf-analyzer \
  --image golf-analyzer-simple \
  --ports 5000 \
  --dns-name-label golf-analyzer
```

## 📈 성능 최적화

### 멀티 스테이지 빌드
```dockerfile
# Dockerfile.optimized
FROM python:3.9-slim as builder
COPY requirements_simple.txt .
RUN pip install --user -r requirements_simple.txt

FROM python:3.9-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
CMD ["python", "app_simple.py"]
```

### 리소스 제한
```yaml
# docker-compose.yml
services:
  golf-analyzer-simple:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🔒 보안 설정

### 비루트 사용자
```dockerfile
# Dockerfile.security
FROM python:3.9-slim
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
WORKDIR /app
COPY . .
CMD ["python", "app_simple.py"]
```

### 환경 변수 보안
```bash
# .env 파일
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
```

## 📞 지원

문제가 발생하거나 추가 도움이 필요하시면 언제든 연락해 주세요!

---

**© 2024 잼나 골프 스윙 분석. All rights reserved.** 