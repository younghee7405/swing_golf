import cv2
import mediapipe as mp
import numpy as np
import math
from PIL import ImageFont, ImageDraw, Image # 한글 텍스트 그리기를 위해 필요

# MediaPipe Pose 설정
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def calc_angle(a, b, c):
    """세 점을 이용하여 각도를 계산합니다 (도)."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    # 두 벡터 (ba, bc) 계산
    ba = a - b
    bc = c - b
    
    # 내적과 벡터 크기를 이용한 코사인 값 계산
    dot_product = np.dot(ba, bc)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    
    if norm_ba == 0 or norm_bc == 0: # 0으로 나누는 경우 방지
        return 0.0
        
    cosine_angle = dot_product / (norm_ba * norm_bc)
    
    # 아크코사인 계산 (값 클리핑으로 부동소수점 오류 방지)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def analyze_swing_metrics(landmarks, frame_width, frame_height):
    """
    MediaPipe 랜드마크를 기반으로 스윙 지표를 분석합니다.
    랜드마크는 정규화된 좌표(0~1)이므로 픽셀 좌표로 변환하여 사용합니다.
    """
    metrics = {}
    feedbacks = []

    def get_landmark_coords(landmark_enum):
        # 랜드마크의 가시성(visibility)이 낮으면 None 반환
        landmark_obj = landmarks[landmark_enum.value]
        if landmark_obj.visibility < 0.6: # 가시성 임계값 설정 (조절 가능)
            return None
        return [int(landmark_obj.x * frame_width), int(landmark_obj.y * frame_height)]

    try:
        # 백스윙 시 왼팔 각도 (LEFT_SHOULDER - LEFT_ELBOW - LEFT_WRIST)
        l_shoulder = get_landmark_coords(mp_pose.PoseLandmark.LEFT_SHOULDER)
        l_elbow = get_landmark_coords(mp_pose.PoseLandmark.LEFT_ELBOW)
        l_wrist = get_landmark_coords(mp_pose.PoseLandmark.LEFT_WRIST)

        if all(p is not None for p in [l_shoulder, l_elbow, l_wrist]):
            left_arm_angle = calc_angle(l_shoulder, l_elbow, l_wrist)
            metrics['left_arm_angle'] = left_arm_angle
            if left_arm_angle > 160: # 거의 펴진 상태
                feedbacks.append("왼팔 각도가 좋습니다! 백스윙 시 곧게 유지됩니다.")
            elif left_arm_angle > 140:
                feedbacks.append("왼팔 각도가 양호합니다.")
            else:
                feedbacks.append("백스윙 시 왼팔이 너무 많이 굽혀졌을 수 있습니다.")
        else:
            feedbacks.append("왼팔 각도 분석에 필요한 랜드마크가 감지되지 않았습니다.")

        # 어깨 회전 (LEFT_SHOULDER - RIGHT_SHOULDER 라인의 수평 기울기)
        # 더 정확한 3D 회전 분석은 3D 랜드마크(z값)와 복잡한 기하학이 필요합니다.
        # 여기서는 2D 기울기로 간접적인 회전 정도를 측정합니다.
        r_shoulder = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER)
        
        if l_shoulder is not None and r_shoulder is not None:
            # 어깨 라인의 수직 차이 (회전 정도를 나타내는 지표 중 하나)
            shoulder_tilt_diff_y = abs(l_shoulder[1] - r_shoulder[1]) # 픽셀 단위
            metrics['shoulder_tilt_diff_y'] = shoulder_tilt_diff_y
            
            # 정규화된 좌표를 사용한 어깨 라인 기울기 (더 안정적)
            norm_l_shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            norm_r_shoulder_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
            norm_shoulder_tilt_diff = abs(norm_l_shoulder_y - norm_r_shoulder_y)
            metrics['norm_shoulder_tilt_diff'] = norm_shoulder_tilt_diff

            if norm_shoulder_tilt_diff < 0.03: # 임계값 조절 필요
                feedbacks.append("어깨 회전이 부족하거나 수평을 유지하지 못할 수 있습니다.")
            else:
                feedbacks.append("어깨 회전이 좋습니다!")
        else:
            feedbacks.append("어깨 회전 분석에 필요한 랜드마크가 감지되지 않았습니다.")
            
        # 엉덩이 회전 (LEFT_HIP - RIGHT_HIP 라인의 수평 기울기)
        # 마찬가지로 2D 간접 측정
        l_hip = get_landmark_coords(mp_pose.PoseLandmark.LEFT_HIP)
        r_hip = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_HIP)

        if l_hip is not None and r_hip is not None:
            norm_l_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
            norm_r_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y
            norm_hip_tilt_diff = abs(norm_l_hip_y - norm_r_hip_y)
            metrics['norm_hip_tilt_diff'] = norm_hip_tilt_diff
            
            if norm_hip_tilt_diff < 0.02: # 임계값 조절 필요
                feedbacks.append("엉덩이 회전이 부족할 수 있습니다.")
            else:
                feedbacks.append("엉덩이 회전이 좋습니다!")
        else:
            feedbacks.append("엉덩이 회전 분석에 필요한 랜드마크가 감지되지 않았습니다.")

    except Exception as e:
        feedbacks.append(f"분석 중 오류 발생: {e}")
        print(f"분석 중 오류: {e}") # 디버깅용

    return metrics, feedbacks

def draw_hangul_text(image, text, position, font_path, font_size=32, color=(0,255,0)):
    """OpenCV 이미지에 한글 텍스트를 그립니다."""
    # OpenCV 이미지를 PIL 이미지로 변환
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"오류: 폰트 파일 '{font_path}'을(를) 찾을 수 없습니다. static/ 폴더에 'malgun.ttf'를 넣어주세요.")
        # 폰트 로드 실패 시 기본 폰트로 대체하거나 에러 메시지 반환
        font = ImageFont.load_default() # 기본 폰트 로드
        text = "폰트 오류: " + text # 사용자에게 폰트 오류임을 알림

    draw.text(position, text, font=font, fill=color)
    
    # PIL 이미지를 다시 OpenCV 이미지로 변환
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def process_video_for_swing_analysis(filepath, output_path, font_path):
    """
    동영상을 분석하고 랜드마크, 각도, 피드백을 오버레이하여 새 동영상으로 저장합니다.
    """
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        return None, f"오류: 입력 동영상 파일을 열 수 없습니다. 경로를 확인하세요: {filepath}"

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 비디오 라이터 설정 (MP4V 코덱)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    if not out.isOpened():
        cap.release()
        return None, f"오류: 출력 동영상 파일을 생성할 수 없습니다. 경로 또는 코덱을 확인하세요: {output_path}" \
                     f" (FourCC: {fourcc}, FPS: {fps}, Size: {frame_width}x{frame_height})"

    print(f"동영상 분석 시작: {filepath}")
    print(f"프레임 크기: {frame_width}x{frame_height}, FPS: {fps}")

    frame_count = 0
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            # BGR 이미지를 RGB로 변환 (MediaPipe는 RGB를 선호)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False # 이미지 쓰기 불가능 설정 (성능 최적화)

            # 포즈 추정 처리
            results = pose.process(image)

            # 이미지 쓰기 가능 설정 및 BGR로 다시 변환
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            current_feedbacks = []
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                
                # 스윙 지표 분석 및 피드백 생성
                metrics, feedbacks = analyze_swing_metrics(results.pose_landmarks.landmark, frame_width, frame_height)
                current_feedbacks.extend(feedbacks)
                
                # 화면에 각도 및 지표 표시 (선택 사항)
                if 'left_arm_angle' in metrics:
                    image = draw_hangul_text(image, f"왼팔 각도: {metrics['left_arm_angle']:.1f} deg", 
                                             (10, 30), font_path, font_size=30, color=(0, 255, 0))
                if 'norm_shoulder_tilt_diff' in metrics:
                    image = draw_hangul_text(image, f"어깨 기울기: {metrics['norm_shoulder_tilt_diff']:.3f}", 
                                             (10, 70), font_path, font_size=30, color=(0, 255, 0))
                # 다른 지표도 필요시 추가

            # 프레임별 피드백 화면에 그리기
            y_offset = 120 # 피드백 시작 Y 좌표
            for i, fb in enumerate(current_feedbacks):
                image = draw_hangul_text(image, fb, (10, y_offset + i * 40), font_path, font_size=28, color=(255, 255, 0)) # 노란색 피드백

            out.write(image)

    cap.release()
    out.release()
    print(f"동영상 분석 완료. 결과가 {output_path}에 저장되었습니다.")
    return output_path, None # 성공 시 출력 경로와 에러 없음 반환