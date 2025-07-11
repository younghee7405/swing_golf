#!/bin/bash

# 골프 스윙 분석기 Docker 배포 스크립트

echo "🚀 골프 스윙 분석기 Docker 배포 시작"

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "📥 Docker 설치: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    echo "📥 Docker Compose 설치: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker 및 Docker Compose 확인 완료"

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down --remove-orphans

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build

# 컨테이너 시작
echo "🚀 컨테이너 시작 중..."
docker-compose up -d

# 상태 확인
echo "📊 컨테이너 상태 확인 중..."
docker-compose ps

echo ""
echo "🎉 배포 완료!"
echo ""
echo "📱 접속 정보:"
echo "   - OpenCV 버전 (권장): http://localhost:5000"
echo "   - MediaPipe 버전: http://localhost:5001"
echo "   - Nginx 프록시: http://localhost:80"
echo ""
echo "📋 유용한 명령어:"
echo "   - 로그 확인: docker-compose logs -f"
echo "   - 컨테이너 중지: docker-compose down"
echo "   - 컨테이너 재시작: docker-compose restart"
echo ""
echo "🔧 문제 해결:"
echo "   - 포트 충돌 시: docker-compose down && docker-compose up -d"
echo "   - 이미지 재빌드: docker-compose build --no-cache"
echo "   - 볼륨 정리: docker-compose down -v" 