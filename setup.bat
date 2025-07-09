@echo off
echo [*] Checking Python...
python --version || (
    echo Python is not installed. Please install Python 3.10 first.
    echo Download link: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    pause
    exit
)

echo [*] Checking Tesseract...
where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo Tesseract is not installed.
    echo Please install Tesseract OCR manually from:
    echo Windows: https://github.com/UB-Mannheim/tesseract/releases
) else (
    echo Tesseract is already installed.
)

echo [*] Creating virtual environment...
python -m venv .venv

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [*] Installing dependencies...
pip install -r requirements.txt

echo [*] Setup complete.
pause
