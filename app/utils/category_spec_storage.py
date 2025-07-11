"""
category_spec_storage.py
────────────────────────────────────────────────────────────
- 크롤링한 카테고리 스펙 데이터를 저장/불러오기 위한 모듈
- 저장 위치: storage/category_spec/
- 파일명: <세부항목명>.json

📌 함수
- save_category_spec(url: str, detail_name: str, data: dict) -> None
- load_category_spec(detail_name: str) -> dict
- category_spec_exists(detail_name: str) -> bool
"""

import json
import re
from pathlib import Path

# =====================================================
# 0️⃣ 전역 설정
# =====================================================
STORAGE_DIR = Path("storage/category_spec")


# =====================================================
# 1️⃣ 파일명 Sanitizer
# =====================================================
def sanitize_filename(detail_name: str) -> str:
    """
    파일명으로 안전하도록 detail_name을 변환
    - 공백은 _로 치환
    - 한글/영문/숫자/_-만 남김
    """
    safe = detail_name.strip()
    safe = re.sub(r"\s+", "_", safe)  # 공백 -> _
    safe = re.sub(r"[^가-힣A-Za-z0-9_-]", "_", safe)  # 허용 문자 외 제거
    safe = re.sub(r"_+", "_", safe).strip("_")  # 연속된 _ 정리
    return safe


# =====================================================
# 2️⃣ 저장 함수
# =====================================================
def save_category_spec(url: str, detail_name: str, data: dict) -> None:
    """
    크롤링한 데이터를 JSON 파일로 저장
    - url: 크롤링한 페이지 URL (로그 용도)
    - detail_name: 저장할 파일명 (확장자 제외)
    - data: 크롤링 데이터 dict
    """
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(detail_name)
    file_path = STORAGE_DIR / f"{filename}.json"

    payload = {
        "url": url,
        "data": data
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"💾 저장 완료: {file_path}")


# =====================================================
# 3️⃣ 불러오기 함수
# =====================================================
def load_category_spec(detail_name: str) -> dict:
    """
    저장된 JSON 파일을 불러와 dict로 반환
    - detail_name: 파일명 (확장자 제외)
    - return: dict ({"url": str, "data": dict})
    """
    filename = sanitize_filename(detail_name)
    file_path = STORAGE_DIR / f"{filename}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"❌ 파일이 존재하지 않습니다: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    print(f"📄 불러오기 완료: {file_path}")
    return payload


# =====================================================
# 4️⃣ 존재 여부 확인 함수
# =====================================================
def category_spec_exists(detail_name: str) -> bool:
    """
    저장된 JSON 파일 존재 여부를 확인
    - detail_name: 파일명 (확장자 제외)
    - return: bool
    """
    filename = sanitize_filename(detail_name)
    file_path = STORAGE_DIR / f"{filename}.json"
    exists = file_path.exists()
    print(f"🔍 파일 존재 여부({file_path}): {exists}")
    return exists
