document.addEventListener('DOMContentLoaded', () => {
    // index.html (업로드 페이지) 관련 로직
    const videoUploadInput = document.getElementById('video-upload-input');
    const fileNameDisplay = document.getElementById('file-name-display');
    const uploadForm = document.getElementById('upload-form');
    const analyzeButton = document.getElementById('analyze-button');

    if (videoUploadInput && fileNameDisplay) {
        videoUploadInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = `선택된 파일: ${this.files[0].name}`;
                fileNameDisplay.style.color = '#3498db';
            } else {
                fileNameDisplay.textContent = '선택된 파일 없음';
                fileNameDisplay.style.color = '#888';
            }
        });
    }

    if (uploadForm && analyzeButton) {
        uploadForm.addEventListener('submit', function() {
            analyzeButton.disabled = true; // 제출 후 버튼 비활성화
            analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 분석 시작 중...';
        });
    }

    // analysis_status.html (분석 상태 페이지) 관련 로직은 해당 HTML 파일 내에 직접 포함되어 있습니다.
    // 이는 Flask의 url_for을 직접 사용하기 위함입니다.
});