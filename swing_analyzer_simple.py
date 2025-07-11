import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import os
import subprocess

def calc_angle(a, b, c):
    """세 점으로 이루어진 각도를 계산합니다."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def detect_person_simple(frame):
    """OpenCV HOG 디텍터를 사용하여 사람을 감지합니다."""
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    # 프레임 크기 조정
    height, width = frame.shape[:2]
    scale = 640 / width
    if scale < 1:
        frame_resized = cv2.resize(frame, (640, int(height * scale)))
    else:
        frame_resized = frame
    
    # 사람 감지
    boxes, weights = hog.detectMultiScale(frame_resized, winStride=(8, 8), padding=(4, 4), scale=1.05)
    
    if len(boxes) > 0:
        # 가장 큰 박스 선택
        largest_box = max(boxes, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_box
        
        # 원본 크기로 좌표 변환
        if scale < 1:
            x = int(x / scale)
            y = int(y / scale)
            w = int(w / scale)
            h = int(h / scale)
        
        return (x, y, w, h)
    return None

def estimate_pose_simple(person_box, frame):
    """간단한 포즈 추정 (사람 박스 기반)"""
    if person_box is None:
        return None
    
    x, y, w, h = person_box
    
    # 간단한 관절 위치 추정
    # 실제로는 더 정교한 알고리즘이 필요하지만, 여기서는 시뮬레이션
    center_x = x + w // 2
    center_y = y + h // 2
    
    # 관절 위치 시뮬레이션
    joints = {
        'left_shoulder': (center_x - w//4, y + h//3),
        'right_shoulder': (center_x + w//4, y + h//3),
        'left_elbow': (center_x - w//3, y + h//2),
        'right_elbow': (center_x + w//3, y + h//2),
        'left_wrist': (center_x - w//2, y + h//2),
        'right_wrist': (center_x + w//2, y + h//2),
        'left_hip': (center_x - w//4, y + 2*h//3),
        'right_hip': (center_x + w//4, y + 2*h//3),
        'left_knee': (center_x - w//4, y + h),
        'right_knee': (center_x + w//4, y + h),
        'left_ankle': (center_x - w//4, y + h),
        'right_ankle': (center_x + w//4, y + h)
    }
    
    return joints

def analyze_swing_simple(joints):
    """간단한 스윙 분석"""
    if joints is None:
        return {
            'left_arm_angle': 0,
            'shoulder_rotation': 0,
            'hip_rotation': 0,
            'spine_angle': 0,
            'swing_phase': 'unknown'
        }
    
    # 관절 좌표 추출
    left_shoulder = joints['left_shoulder']
    right_shoulder = joints['right_shoulder']
    left_elbow = joints['left_elbow']
    left_wrist = joints['left_wrist']
    left_hip = joints['left_hip']
    right_hip = joints['right_hip']
    
    # 각도 계산
    left_arm_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
    shoulder_rotation = abs(left_shoulder[1] - right_shoulder[1])
    hip_rotation = abs(left_hip[1] - right_hip[1])
    spine_angle = calc_angle(left_shoulder, left_hip, (left_hip[0], left_hip[1] + 100))
    
    # 스윙 단계 판단 (간단한 시뮬레이션)
    wrist_height = left_wrist[1]
    shoulder_height = left_shoulder[1]
    
    if wrist_height < shoulder_height - 20:
        swing_phase = "backswing"
    elif wrist_height > shoulder_height + 20:
        swing_phase = "downswing"
    else:
        swing_phase = "setup"
    
    return {
        'left_arm_angle': left_arm_angle,
        'shoulder_rotation': shoulder_rotation,
        'hip_rotation': hip_rotation,
        'spine_angle': spine_angle,
        'swing_phase': swing_phase
    }

def give_feedback_simple(analysis_data):
    """간단한 피드백 제공"""
    feedbacks = []
    solutions = []
    
    left_arm_angle = analysis_data['left_arm_angle']
    shoulder_rotation = analysis_data['shoulder_rotation']
    
    if left_arm_angle < 140:
        feedbacks.append("백스윙 시 왼팔이 너무 많이 굽혀졌어요.")
        solutions.append("백스윙 시 왼팔을 최대한 곧게 펴는 연습을 해보세요.")
    else:
        feedbacks.append("왼팔 각도가 좋습니다!")
        solutions.append("현재 왼팔 각도를 유지하세요.")
    
    if shoulder_rotation < 5:
        feedbacks.append("어깨 회전이 부족합니다.")
        solutions.append("백스윙 때 어깨가 충분히 회전되도록 상체를 더 돌려보세요.")
    else:
        feedbacks.append("어깨 회전이 적절합니다!")
        solutions.append("현재 어깨 회전을 유지하세요.")
    
    return feedbacks, solutions

def draw_analysis_simple(image, joints, analysis_data, feedbacks):
    """분석 결과를 화면에 표시"""
    if joints:
        # 관절 연결선 그리기
        connections = [
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip')
        ]
        
        for start_joint, end_joint in connections:
            if start_joint in joints and end_joint in joints:
                cv2.line(image, joints[start_joint], joints[end_joint], (0, 255, 0), 2)
        
        # 관절점 그리기
        for joint_name, joint_pos in joints.items():
            cv2.circle(image, joint_pos, 5, (255, 0, 0), -1)
    
    # 분석 정보 표시
    y_offset = 30
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 스윙 단계
    cv2.putText(image, f"Swing Phase: {analysis_data['swing_phase']}", 
                (10, y_offset), font, 0.7, (255, 255, 0), 2)
    y_offset += 30
    
    # 각도 정보
    cv2.putText(image, f"Left Arm Angle: {analysis_data['left_arm_angle']:.1f}°", 
                (10, y_offset), font, 0.7, (0, 255, 0), 2)
    y_offset += 30
    
    cv2.putText(image, f"Shoulder Rotation: {analysis_data['shoulder_rotation']:.1f}", 
                (10, y_offset), font, 0.7, (0, 255, 0), 2)
    y_offset += 30
    
    # 피드백 표시
    for i, feedback in enumerate(feedbacks[:2]):
        cv2.putText(image, feedback, (10, y_offset + i*25), font, 0.6, (255, 255, 255), 2)
    
    return image

def draw_hangul_text(image, text, position, font_path='MALGUN.TTF', font_size=32, color=(0,255,0)):
    """한글 텍스트를 이미지에 그립니다."""
    try:
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, font=font, fill=color)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    except:
        # 폰트가 없을 경우 기본 폰트 사용
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return image

def reencode_mp4(input_path, output_path):
    """MP4 파일을 재인코딩합니다."""
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

def process_video_simple(input_path, output_path, font_path='MALGUN.TTF'):
    """OpenCV만을 사용한 간단한 동영상 분석"""
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
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 사람 감지
        person_box = detect_person_simple(frame)
        
        if person_box:
            # 포즈 추정
            joints = estimate_pose_simple(person_box, frame)
            
            if joints:
                # 스윙 분석
                analysis_data = analyze_swing_simple(joints)
                feedbacks, solutions = give_feedback_simple(analysis_data)
                
                feedbacks_all.append(feedbacks)
                solutions_all.append(solutions)
                
                # 분석 결과 화면에 표시
                frame = draw_analysis_simple(frame, joints, analysis_data, feedbacks)
        
        out.write(frame)
    
    cap.release()
    out.release()
    reencode_mp4(output_path, output_path)
    
    # 마지막 프레임의 피드백 반환
    last_feedbacks = feedbacks_all[-1] if feedbacks_all else []
    last_solutions = solutions_all[-1] if solutions_all else []
    
    return output_path, None, last_feedbacks, last_solutions 