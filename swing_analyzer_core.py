import cv2
import mediapipe as mp
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import os
import subprocess
import math

def calc_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def calc_distance(a, b):
    """두 점 사이의 거리를 계산합니다."""
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)

def detect_swing_phase(landmarks, frame_count):
    """스윙 단계를 감지합니다."""
    mp_pose = mp.solutions.pose
    
    # 핵심 관절 포인트 추출
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    
    # 스윙 단계 판단 (간단한 예시)
    wrist_height = (left_wrist[1] + right_wrist[1]) / 2
    shoulder_height = (left_shoulder[1] + right_shoulder[1]) / 2
    
    if wrist_height < shoulder_height - 0.1:
        return "backswing"
    elif wrist_height > shoulder_height + 0.1:
        return "downswing"
    else:
        return "setup"

def analyze_swing_comprehensive(landmarks, swing_phase="setup"):
    """포괄적인 스윙 분석을 수행합니다."""
    mp_pose = mp.solutions.pose
    
    # 모든 필요한 관절 포인트 추출
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                  landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
    
    # 1. 팔 각도 분석
    left_arm_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
    right_arm_angle = calc_angle(right_shoulder, right_elbow, right_wrist)
    
    # 2. 어깨 회전 분석
    shoulder_rotation = abs(left_shoulder[1] - right_shoulder[1])
    shoulder_tilt = abs(left_shoulder[0] - right_shoulder[0])
    
    # 3. 엉덩이 회전 분석
    hip_rotation = abs(left_hip[1] - right_hip[1])
    
    # 4. 무릎 각도 분석
    left_knee_angle = calc_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calc_angle(right_hip, right_knee, right_ankle)
    
    # 5. 척추 기울기 분석
    spine_angle = calc_angle(left_shoulder, left_hip, left_ankle)
    
    # 6. 팔꿈치 위치 분석
    elbow_position = (left_elbow[0] + right_elbow[0]) / 2
    
    # 7. 손목 높이 분석
    wrist_height_relative = (left_wrist[1] + right_wrist[1]) / 2 - (left_shoulder[1] + right_shoulder[1]) / 2
    
    return {
        'left_arm_angle': left_arm_angle,
        'right_arm_angle': right_arm_angle,
        'shoulder_rotation': shoulder_rotation,
        'shoulder_tilt': shoulder_tilt,
        'hip_rotation': hip_rotation,
        'left_knee_angle': left_knee_angle,
        'right_knee_angle': right_knee_angle,
        'spine_angle': spine_angle,
        'elbow_position': elbow_position,
        'wrist_height_relative': wrist_height_relative,
        'swing_phase': swing_phase
    }

def give_comprehensive_feedback(analysis_data):
    """포괄적인 피드백을 제공합니다."""
    feedbacks = []
    solutions = []
    scores = []
    
    # 1. 왼팔 각도 분석
    left_arm_angle = analysis_data['left_arm_angle']
    if left_arm_angle < 140:
        feedbacks.append("백스윙 시 왼팔이 너무 많이 굽혀졌어요.")
        solutions.append("백스윙 시 왼팔을 최대한 곧게 펴는 연습을 해보세요.")
        scores.append(60)
    elif left_arm_angle > 180:
        feedbacks.append("왼팔이 너무 뻗어있습니다.")
        solutions.append("왼팔을 자연스럽게 구부려보세요.")
        scores.append(70)
    else:
        feedbacks.append("왼팔 각도가 좋습니다!")
        solutions.append("현재 왼팔 각도를 유지하세요.")
        scores.append(90)
    
    # 2. 어깨 회전 분석
    shoulder_rotation = analysis_data['shoulder_rotation']
    if shoulder_rotation < 0.05:
        feedbacks.append("어깨 회전이 부족합니다.")
        solutions.append("백스윙 때 어깨가 충분히 회전되도록 상체를 더 돌려보세요.")
        scores.append(50)
    elif shoulder_rotation > 0.15:
        feedbacks.append("어깨 회전이 과도합니다.")
        solutions.append("어깨 회전을 조금 줄여보세요.")
        scores.append(75)
    else:
        feedbacks.append("어깨 회전이 적절합니다!")
        solutions.append("현재 어깨 회전을 유지하세요.")
        scores.append(85)
    
    # 3. 엉덩이 회전 분석
    hip_rotation = analysis_data['hip_rotation']
    if hip_rotation < 0.03:
        feedbacks.append("엉덩이 회전이 부족합니다.")
        solutions.append("하체 회전을 더 강화해보세요.")
        scores.append(60)
    else:
        feedbacks.append("엉덩이 회전이 좋습니다!")
        solutions.append("현재 하체 회전을 유지하세요.")
        scores.append(85)
    
    # 4. 무릎 각도 분석
    left_knee_angle = analysis_data['left_knee_angle']
    if left_knee_angle < 140:
        feedbacks.append("무릎이 너무 많이 굽혀졌습니다.")
        solutions.append("무릎을 조금 더 펴보세요.")
        scores.append(70)
    elif left_knee_angle > 180:
        feedbacks.append("무릎이 너무 뻗어있습니다.")
        solutions.append("무릎을 자연스럽게 구부려보세요.")
        scores.append(75)
    else:
        feedbacks.append("무릎 각도가 적절합니다!")
        solutions.append("현재 무릎 각도를 유지하세요.")
        scores.append(90)
    
    # 5. 척추 기울기 분석
    spine_angle = analysis_data['spine_angle']
    if spine_angle < 150:
        feedbacks.append("상체가 너무 숙여졌습니다.")
        solutions.append("상체를 조금 더 세워보세요.")
        scores.append(65)
    elif spine_angle > 180:
        feedbacks.append("상체가 너무 뻗어있습니다.")
        solutions.append("상체를 자연스럽게 구부려보세요.")
        scores.append(70)
    else:
        feedbacks.append("상체 자세가 좋습니다!")
        solutions.append("현재 상체 자세를 유지하세요.")
        scores.append(90)
    
    # 6. 팔꿈치 위치 분석
    elbow_position = analysis_data['elbow_position']
    if elbow_position < 0.3:
        feedbacks.append("팔꿈치가 너무 안쪽에 있습니다.")
        solutions.append("팔꿈치를 바깥쪽으로 조정해보세요.")
        scores.append(75)
    elif elbow_position > 0.7:
        feedbacks.append("팔꿈치가 너무 바깥쪽에 있습니다.")
        solutions.append("팔꿈치를 안쪽으로 조정해보세요.")
        scores.append(75)
    else:
        feedbacks.append("팔꿈치 위치가 적절합니다!")
        solutions.append("현재 팔꿈치 위치를 유지하세요.")
        scores.append(85)
    
    # 7. 스윙 단계별 특별 피드백
    swing_phase = analysis_data['swing_phase']
    if swing_phase == "backswing":
        feedbacks.append("백스윙 단계입니다.")
        solutions.append("클럽을 천천히 들어올리세요.")
        scores.append(80)
    elif swing_phase == "downswing":
        feedbacks.append("다운스윙 단계입니다.")
        solutions.append("힘을 조절하여 스윙하세요.")
        scores.append(80)
    
    return feedbacks, solutions, scores

def draw_comprehensive_analysis(image, analysis_data, feedbacks, font_path='malgun.ttf'):
    """포괄적인 분석 결과를 화면에 표시합니다."""
    # 분석 데이터 표시
    y_offset = 30
    font_size = 24
    
    # 스윙 단계 표시
    phase_text = f"스윙 단계: {analysis_data['swing_phase']}"
    image = draw_hangul_text(image, phase_text, (10, y_offset), font_path=font_path, font_size=font_size, color=(255, 255, 0))
    y_offset += 40
    
    # 주요 각도 표시
    angle_text = f"왼팔 각도: {analysis_data['left_arm_angle']:.1f}°"
    image = draw_hangul_text(image, angle_text, (10, y_offset), font_path=font_path, font_size=font_size, color=(0, 255, 0))
    y_offset += 40
    
    shoulder_text = f"어깨 회전: {analysis_data['shoulder_rotation']:.3f}"
    image = draw_hangul_text(image, shoulder_text, (10, y_offset), font_path=font_path, font_size=font_size, color=(0, 255, 0))
    y_offset += 40
    
    hip_text = f"엉덩이 회전: {analysis_data['hip_rotation']:.3f}"
    image = draw_hangul_text(image, hip_text, (10, y_offset), font_path=font_path, font_size=font_size, color=(0, 255, 0))
    y_offset += 40
    
    # 피드백 표시
    y_offset += 20
    for i, feedback in enumerate(feedbacks[:3]):  # 최대 3개만 표시
        image = draw_hangul_text(image, feedback, (10, y_offset + i*30), font_path=font_path, font_size=20, color=(255, 255, 255))
    
    return image

def draw_hangul_text(image, text, position, font_path='malgun.ttf', font_size=32, color=(0,255,0)):
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        # 폰트가 없을 경우 기본 폰트 사용
        font = ImageFont.load_default()
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def reencode_mp4(input_path, output_path):
    temp_path = output_path + '.tmp.mp4'
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-vcodec', 'libx264', '-acodec', 'aac', '-strict', '-2', temp_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.replace(temp_path, output_path)
    except Exception as e:
        print(f"ffmpeg 재인코딩 실패: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

def process_video_for_swing_analysis(input_path, output_path, font_path='malgun.ttf'):
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return None, "동영상 파일을 열 수 없습니다.", [], []
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    
    feedbacks_all = []
    solutions_all = []
    scores_all = []
    frame_count = 0
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                # 스윙 단계 감지
                swing_phase = detect_swing_phase(results.pose_landmarks.landmark, frame_count)
                
                # 포괄적인 분석 수행
                analysis_data = analyze_swing_comprehensive(results.pose_landmarks.landmark, swing_phase)
                feedbacks, solutions, scores = give_comprehensive_feedback(analysis_data)
                
                feedbacks_all.append(feedbacks)
                solutions_all.append(solutions)
                scores_all.append(scores)
                
                # 포즈 랜드마크 그리기
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # 분석 결과 화면에 표시
                image = draw_comprehensive_analysis(image, analysis_data, feedbacks, font_path)
            
            out.write(image)
            frame_count += 1
    
    cap.release()
    out.release()
    reencode_mp4(output_path, output_path)
    
    # 마지막 프레임의 피드백 반환
    last_feedbacks = feedbacks_all[-1] if feedbacks_all else []
    last_solutions = solutions_all[-1] if solutions_all else []
    last_scores = scores_all[-1] if scores_all else []
    
    return output_path, None, last_feedbacks, last_solutions 