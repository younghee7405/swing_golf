# 🏌️‍♂️ 골프 스윙 분석기

골프 스윙을 분석하고 개선 방안을 제시하는 AI 기반 웹 애플리케이션입니다.

## ✨ 주요 기능

### 🎯 **분석 정확도 향상**
- **7가지 골프 스윙 요소** 분석
- **스윙 단계별 감지** (백스윙, 다운스윙, 임팩트)
- **실시간 각도 측정** 및 피드백

### 📊 **실시간 피드백 강화**
- 분석 진행률 실시간 표시
- 단계별 분석 상태 시각화
- 실시간 피드백 업데이트

### 🔍 **포괄적인 스윙 분석**
- 왼팔/오른팔 각도 분석
- 어깨/엉덩이 회전 분석
- 척추 기울기 및 자세 분석
- 무릎 각도 및 팔꿈치 위치 분석

## 🚀 빠른 시작

### 방법 1: OpenCV 버전 (권장 - MediaPipe 설치 문제 해결)

```bash
# 1. 패키지 설치
pip install -r requirements_simple.txt

# 2. 애플리케이션 실행
python app_simple.py

# 3. 브라우저에서 접속
# http://localhost:5000
```

### 방법 2: MediaPipe 버전 (고급 분석)

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 애플리케이션 실행
python app.py

# 3. 브라우저에서 접속
# http://localhost:5000
```

## 📋 시스템 요구사항

- **Python**: 3.7-3.11 (3.9 권장)
- **운영체제**: Windows 10/11, Linux, macOS
- **메모리**: 최소 4GB RAM
- **저장공간**: 1GB 이상
- **웹캠** 또는 **동영상 파일** (MP4, MOV, AVI)

## 🔧 설치 문제 해결

### MediaPipe 설치 실패 시

1. **Python 버전 확인**
   ```bash
   python --version  # 3.7-3.11 권장
   ```

2. **OpenCV 버전 사용** (권장)
   ```bash
   pip install -r requirements_simple.txt
   python app_simple.py
   ```

3. **대안 해결 방법**
   - Python 3.9 설치
   - Visual Studio Build Tools 설치
   - Microsoft Visual C++ Redistributable 설치

## 📁 프로젝트 구조

```
motion/
├── app.py                    # MediaPipe 버전 메인 앱
├── app_simple.py             # OpenCV 버전 메인 앱
├── swing_analyzer_core.py    # MediaPipe 분석 엔진
├── swing_analyzer_simple.py  # OpenCV 분석 엔진
├── requirements.txt          # MediaPipe 버전 의존성
├── requirements_simple.txt   # OpenCV 버전 의존성
├── templates/               # HTML 템플릿
├── static/                  # CSS, JS, 폰트 파일
├── uploads/                 # 업로드된 동영상
└── results/                 # 분석 결과 동영상
```

## 🎯 분석 요소

### 1. **팔 각도 분석**
- 왼팔 각도: 백스윙 시 곧게 펴기
- 오른팔 각도: 자연스러운 구부림

### 2. **어깨 회전 분석**
- 어깨 회전량 측정
- 상체 회전 최적화

### 3. **엉덩이 회전 분석**
- 하체 회전량 측정
- 하체와 상체의 조화

### 4. **척추 기울기 분석**
- 상체 자세 분석
- 자연스러운 스윙 자세

### 5. **무릎 각도 분석**
- 무릎 구부림 정도
- 안정적인 스윙 자세

### 6. **팔꿈치 위치 분석**
- 팔꿈치 위치 최적화
- 클럽 컨트롤 개선

### 7. **스윙 단계 감지**
- 백스윙, 다운스윙, 임팩트 단계별 분석

## 🔄 사용 방법

1. **동영상 업로드**
   - 정면 또는 측면에서 촬영된 골프 스윙 동영상
   - MP4, MOV, AVI 형식 지원

2. **실시간 분석**
   - 분석 진행률 실시간 확인
   - 단계별 분석 상태 표시

3. **결과 확인**
   - 분석된 동영상 재생
   - 상세한 피드백 및 개선 방안
   - 분석 데이터 요약

## 🛠️ 개발자 정보

### 기술 스택
- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, MediaPipe (선택사항)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI/UX**: 반응형 디자인, 실시간 업데이트

### 주요 개선사항
- ✅ 분석 정확도 향상
- ✅ 실시간 피드백 강화
- ✅ 더 많은 스윙 요소 분석
- ✅ 사용자 경험 개선

## 📞 지원

문제가 발생하거나 개선 제안이 있으시면 언제든 연락해 주세요!

---

**© 2024 잼나 골프 스윙 분석. All rights reserved.** 