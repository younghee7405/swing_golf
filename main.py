import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calc_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def analyze_swing(landmarks):
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    left_arm_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    shoulder_rotation = abs(left_shoulder[1] - right_shoulder[1])
    return left_arm_angle, shoulder_rotation

def give_feedback(left_arm_angle, shoulder_rotation):
    feedbacks = []
    if left_arm_angle < 140:
        feedbacks.append("백스윙 시 왼팔이 너무 많이 굽혀졌어요.")
    else:
        feedbacks.append("왼팔 각도가 좋습니다!")
    if shoulder_rotation < 0.05:
        feedbacks.append("어깨 회전이 부족합니다.")
    else:
        feedbacks.append("어깨 회전이 충분합니다!")
    return feedbacks

st.title("골프 스윙 분석기")
st.write("동영상 파일을 업로드하거나 웹캠을 사용할 수 있습니다.")

video_file = st.file_uploader("동영상 파일 업로드", type=["mp4", "avi", "mov"])
use_webcam = st.button("웹캠으로 분석하기")

if video_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    cap = cv2.VideoCapture(tfile.name)
elif use_webcam:
    cap = cv2.VideoCapture(0)
else:
    cap = None

if cap is not None:
    stframe = st.empty()
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                left_arm_angle, shoulder_rotation = analyze_swing(results.pose_landmarks.landmark)
                feedbacks = give_feedback(left_arm_angle, shoulder_rotation)
                cv2.putText(image, f'Left Arm Angle: {int(left_arm_angle)}', (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                y0 = 90
                for i, fb in enumerate(feedbacks):
                    cv2.putText(image, fb, (30, y0 + i*40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2, cv2.LINE_AA)
            stframe.image(image, channels="RGB")
    cap.release() 