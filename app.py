import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import tempfile # 임시 파일 생성을 위해 필요
import threading # 비동기 처리를 위해 필요 (간단한 예시)
import subprocess
import time

# 핵심 분석 로직 모듈 임포트
from swing_analyzer_core import process_video_for_swing_analysis, analyze_swing_comprehensive, give_comprehensive_feedback

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' # flash 메시지를 위해 필요, 실제 배포 시에는 복잡하게 변경

# 업로드 및 결과 폴더 설정
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
FONT_PATH = os.path.join('static', 'MALGUN.TTF') # 한글 폰트 경로

# 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# 분석 작업 상태를 저장할 딕셔너리 (간단한 예시, 실제는 Redis 등 사용)
analysis_status = {} # {session_id: {"status": "processing/completed/failed", "result_filename": None, "feedback": [], "solutions": [], "analysis_data": {}, "progress": 0}}

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

    if file and file.filename.endswith(('.mp4', '.mov', '.avi')): # 지원하는 동영상 형식
        # 임시 파일로 저장하여 분석
        # 사용자 ID 또는 세션 ID를 사용하여 고유한 파일명 생성 권장
        session_id = request.cookies.get('session_id', 'default_user') # 임시 세션 ID
        unique_filename = f"{session_id}_{os.path.basename(file.filename)}"
        
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # 분석 결과 저장 경로
        result_filename = f"analyzed_{unique_filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)

        # 분석 작업 시작 (비동기 처리 시뮬레이션)
        # 실제 환경에서는 Celery, RQ 등의 Task Queue를 사용해야 합니다.
        # 여기서는 간단한 스레딩으로 웹 요청을 블록하지 않도록 합니다.
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
                time.sleep(1)  # 시뮬레이션
                
                analysis_status[session_id]["progress"] = 50
                time.sleep(1)  # 시뮬레이션
                
                output_video_path, error_msg, feedbacks, solutions = process_video_for_swing_analysis(filepath, result_path, FONT_PATH)
                
                analysis_status[session_id]["progress"] = 75
                
                if output_video_path:
                    analysis_status[session_id]["status"] = "completed"
                    analysis_status[session_id]["result_filename"] = os.path.basename(output_video_path)
                    analysis_status[session_id]["feedback"] = feedbacks
                    analysis_status[session_id]["solutions"] = solutions
                    analysis_status[session_id]["progress"] = 100
                    
                    # 분석 데이터 시뮬레이션 (실제로는 분석 과정에서 수집)
                    analysis_status[session_id]["analysis_data"] = {
                        "swing_phase": "completed",
                        "left_arm_angle": 165.5,
                        "shoulder_rotation": 0.08,
                        "hip_rotation": 0.05,
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

            # 원본 동영상 파일 삭제 (선택 사항)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"원본 동영상 삭제됨: {filepath}")

        # 스레드 시작
        thread = threading.Thread(target=run_analysis_in_thread)
        thread.start()

        # 분석 시작 메시지를 반환하고, 클라이언트는 상태를 폴링하도록 함
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
    
    # 실시간 피드백 시뮬레이션 (실제로는 분석 과정에서 실시간으로 업데이트)
    if status_info.get("status") == "processing":
        # 진행 중일 때 실시간 데이터 시뮬레이션
        import random
        status_info["analysis_data"] = {
            "swing_phase": random.choice(["setup", "backswing", "downswing"]),
            "left_arm_angle": random.uniform(140, 180),
            "shoulder_rotation": random.uniform(0.03, 0.12),
            "hip_rotation": random.uniform(0.02, 0.08),
            "spine_angle": random.uniform(150, 175),
            "elbow_position": random.uniform(0.3, 0.7)
        }
        
        # 실시간 피드백 시뮬레이션
        feedbacks, solutions, scores = give_comprehensive_feedback(status_info["analysis_data"])
        status_info["feedback"] = feedbacks[:3]  # 최대 3개만 표시
    
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

def reencode_mp4(input_path, output_path):
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-vcodec', 'libx264', '-acodec', 'aac', '-strict', '-2', output_path
    ]
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)