import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import tempfile
import threading
import subprocess
import time

# OpenCV만 사용하는 분석 모듈 임포트
from swing_analyzer_simple import process_video_simple, analyze_swing_simple, give_feedback_simple

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# 업로드 및 결과 폴더 설정
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
FONT_PATH = os.path.join('static', 'MALGUN.TTF')

# 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# 분석 작업 상태를 저장할 딕셔너리
analysis_status = {}

@app.route('/', methods=['GET'])
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/upload_and_analyze', methods=['POST'])
def upload_and_analyze():
    """동영상을 업로드하고 분석을 시작합니다."""
    if 'video' not in request.files:
        flash('동영상 파일이 없습니다.')
        return redirect(url_for('index'))

    file = request.files['video']
    if file.filename == '':
        flash('파일을 선택해주세요.')
        return redirect(url_for('index'))

    if file and file.filename and file.filename.endswith(('.mp4', '.mov', '.avi')):
        # 세션 ID 생성
        session_id = request.cookies.get('session_id', 'default_user')
        unique_filename = f"{session_id}_{os.path.basename(file.filename)}"
        
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # 분석 결과 저장 경로
        result_filename = f"analyzed_{unique_filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)

        # 분석 작업 시작
        analysis_status[session_id] = {
            "status": "processing", 
            "result_filename": None, 
            "feedback": [], 
            "solutions": [], 
            "analysis_data": {},
            "progress": 0,
            "start_time": time.time()
        }
        
        print(f"분석 시작: {filepath}")
        
        # 스레드에서 분석 함수 실행
        def run_analysis_in_thread():
            global analysis_status
            try:
                # 진행률 업데이트
                analysis_status[session_id]["progress"] = 25
                time.sleep(1)
                
                analysis_status[session_id]["progress"] = 50
                time.sleep(1)
                
                # OpenCV 기반 분석 실행
                output_video_path, error_msg, feedbacks, solutions = process_video_simple(filepath, result_path, FONT_PATH)
                
                analysis_status[session_id]["progress"] = 75
                
                if output_video_path:
                    analysis_status[session_id]["status"] = "completed"
                    analysis_status[session_id]["result_filename"] = os.path.basename(output_video_path)
                    analysis_status[session_id]["feedback"] = feedbacks
                    analysis_status[session_id]["solutions"] = solutions
                    analysis_status[session_id]["progress"] = 100
                    
                    # 분석 데이터 시뮬레이션
                    analysis_status[session_id]["analysis_data"] = {
                        "swing_phase": "completed",
                        "left_arm_angle": 165.5,
                        "shoulder_rotation": 8.2,
                        "hip_rotation": 5.1,
                        "spine_angle": 165.0,
                        "elbow_position": 0.45
                    }
                else:
                    analysis_status[session_id]["status"] = "failed"
                    analysis_status[session_id]["message"] = error_msg
                print(f"분석 완료: {analysis_status[session_id]['status']}")
            except Exception as e:
                analysis_status[session_id]["status"] = "failed"
                analysis_status[session_id]["message"] = f"분석 중 예기치 않은 오류 발생: {e}"
                print(f"분석 중 예기치 않은 오류: {e}")
                import traceback
                traceback.print_exc()

            # 원본 동영상 파일 삭제
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"원본 동영상 삭제됨: {filepath}")

        # 스레드 시작
        thread = threading.Thread(target=run_analysis_in_thread)
        thread.start()

        flash('동영상 분석을 시작했습니다. 잠시 후 결과 페이지에서 확인해주세요.')
        return redirect(url_for('analysis_status_page', session_id=session_id))
    else:
        flash('지원하지 않는 파일 형식입니다. MP4, MOV, AVI 파일을 업로드해주세요.')
        return redirect(url_for('index'))

@app.route('/analysis_status/<session_id>')
def analysis_status_page(session_id):
    """분석 진행 상황을 보여주는 페이지."""
    status_info = analysis_status.get(session_id, {"status": "not_found", "message": "분석 정보를 찾을 수 없습니다."})
    return render_template('analysis_status.html', session_id=session_id, status_info=status_info)

@app.route('/get_analysis_status/<session_id>')
def get_analysis_status(session_id):
    """클라이언트가 분석 상태를 폴링하기 위한 API."""
    status_info = analysis_status.get(session_id, {"status": "not_found", "message": "분석 정보를 찾을 수 없습니다."})
    
    # 실시간 피드백 시뮬레이션
    if status_info.get("status") == "processing":
        import random
        status_info["analysis_data"] = {
            "swing_phase": random.choice(["setup", "backswing", "downswing"]),
            "left_arm_angle": random.uniform(140, 180),
            "shoulder_rotation": random.uniform(3, 12),
            "hip_rotation": random.uniform(2, 8),
            "spine_angle": random.uniform(150, 175),
            "elbow_position": random.uniform(0.3, 0.7)
        }
        
        # 실시간 피드백 시뮬레이션
        feedbacks, solutions = give_feedback_simple(status_info["analysis_data"])
        status_info["feedback"] = feedbacks[:3]
    
    return jsonify(status_info)

@app.route('/result/<filename>')
def result(filename):
    session_id = request.cookies.get('session_id', 'default_user')
    feedbacks = analysis_status.get(session_id, {}).get('feedback', [])
    solutions = analysis_status.get(session_id, {}).get('solutions', [])
    analysis_data = analysis_status.get(session_id, {}).get('analysis_data', {})
    return render_template('result.html', filename=filename, feedbacks=feedbacks, solutions=solutions, analysis_data=analysis_data, zip=zip)

@app.route('/results/<filename>')
def serve_result_video(filename):
    """분석된 동영상 파일을 제공합니다."""
    return send_from_directory(RESULT_FOLDER, filename)

if __name__ == '__main__':
    print("🚀 골프 스윙 분석기 (OpenCV 버전) 시작")
    print("📝 MediaPipe 없이 OpenCV만으로 작동합니다.")
    print("🌐 브라우저에서 http://localhost:5000 으로 접속하세요.")
    app.run(debug=True, host='0.0.0.0', port=5000) 