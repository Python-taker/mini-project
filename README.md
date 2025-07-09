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

## ✅ 요약
- `.bat` → Windows 전용: Python, Tesseract 체크 & 안내
- `.sh` → Linux/macOS: Python, Tesseract 체크 & 안내
- `README.md` → 링크와 명령어 명시

---
