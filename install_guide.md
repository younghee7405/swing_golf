# 골프 스윙 분석기 설치 가이드

## MediaPipe 설치 문제 해결

### 방법 1: 특정 버전 설치 (권장)
```bash
pip install mediapipe==0.10.8
```

### 방법 2: Python 버전 확인 후 설치
MediaPipe는 Python 3.7-3.11을 지원합니다.
```bash
python --version
pip install mediapipe
```

### 방법 3: 가상환경에서 설치
```bash
# 가상환경 생성
python -m venv venv_golf

# Windows에서 가상환경 활성화
venv_golf\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 방법 4: 대안 패키지 사용
MediaPipe 설치가 불가능한 경우, OpenCV만으로도 기본적인 분석이 가능합니다.

## 전체 설치 과정

1. **Python 버전 확인**
   ```bash
   python --version  # 3.7-3.11 권장
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv_golf
   venv_golf\Scripts\activate  # Windows
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **FFmpeg 설치 (동영상 처리용)**
   - Windows: https://ffmpeg.org/download.html
   - 또는: `choco install ffmpeg` (Chocolatey 사용 시)

5. **애플리케이션 실행**
   ```bash
   python app.py
   ```

## 문제 해결

### MediaPipe 설치 실패 시
1. Python 버전을 3.9로 다운그레이드
2. Visual Studio Build Tools 설치
3. Microsoft Visual C++ Redistributable 설치

### 대안: OpenCV만 사용
MediaPipe 대신 OpenCV의 HOG 디텍터를 사용할 수 있습니다.
```python
# swing_analyzer_core.py에서 MediaPipe 대신 OpenCV 사용
import cv2
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
```

## 시스템 요구사항

- Python 3.7-3.11
- Windows 10/11 (또는 Linux/Mac)
- 최소 4GB RAM
- 웹캠 또는 동영상 파일 