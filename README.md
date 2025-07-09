# mini-project
SSAFY 2025.07.09 ~ 2025.07.11
# Mini-Project Setup Guide

## 📦 Requirements
- Python 3.10.x
- Tesseract OCR

---

## 🔷 Windows
✅ Python 3.10 다운로드:  
👉 [https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)

✅ Tesseract OCR 다운로드:  
👉 [https://github.com/UB-Mannheim/tesseract/releases](https://github.com/UB-Mannheim/tesseract/releases)

설치 후 Tesseract 경로를 환경 변수 `PATH`에 추가해야 합니다. (보통 자동 설정됩니다.)

---

## 🔷 Linux
✅ Python 3.10: 대부분 기본 설치됨. 없을 경우:
```bash
sudo apt install python3.10 python3.10-venv
```

✅ Tesseract OCR 설치:
```bash
sudo apt update
sudo apt install tesseract-ocr
```

---

🚀 Setup
## 🔷 Windows
PowerShell이나 CMD에서:
```cmd
setup.bat
```

## 🔷 Linux / macOS
터미널에서:
```bash
bash setup.sh
```

---

📌 Notes
- .venv 안에 가상환경이 생성됩니다.
- requirements.txt로 필요한 패키지가 자동 설치됩니다.

---

## 환경 변수 설정

루트 디렉토리에 `.env` 파일을 만들어 아래와 같이 작성해 주세요:

```bash
KAKAO_REST_API_KEY=your-kakao-rest-api-key
OPENAI_API_KEY=your-openai-api-key
UPSTAGE_SOLAR_PRO_API_KEY=your-upstage-api-key
```

```bash
`.env` 파일은 민감한 정보가 포함되므로 절대 깃에 올리지 마세요.
프로젝트를 실행하기 전에 반드시 `.env` 파일을 생성해야 합니다.
```

---

## 설정 파일

`config/settings.json`에 BASE_URL만 작성하세요:

```json
{
  "BASE_URL": "https://your-ngrok-url.ngrok-free.app"
}
```

`storage/tokens.json` 파일은 서버가 자동 생성하며, 유저별 `access_token` 정보를 저장합니다. 
git에 업로드하지 않도록 주의하세요.

---

## ✅ 요약
- `.bat` → Windows 전용: Python, Tesseract 체크 & 안내
- `.sh` → Linux/macOS: Python, Tesseract 체크 & 안내
- `README.md` → 링크와 명령어 명시

---
