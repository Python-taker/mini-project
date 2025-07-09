#!/bin/bash

echo "[*] Checking Python..."
python3.10 --version || {
    echo "Python 3.10 is not installed. Please install it first:"
    echo "https://www.python.org/downloads/release/python-31011/"
    exit 1
}

echo "[*] Checking Tesseract..."
if ! command -v tesseract &> /dev/null
then
    echo "Tesseract OCR is not installed."
    echo "Please install Tesseract OCR manually:"
    echo "Linux (Debian/Ubuntu): sudo apt install tesseract-ocr"
    echo "macOS (Homebrew): brew install tesseract"
else
    echo "Tesseract is already installed."
fi

echo "[*] Creating virtual environment..."
python3.10 -m venv .venv

echo "[*] Activating virtual environment..."
source .venv/bin/activate

echo "[*] Installing dependencies..."
pip install -r requirements.txt

echo "[*] Setup complete."
