"""
category_url_resolver.py
──────────────────────────────
- 중간키 + 세부항목 쌍으로 크롤링 데이터에서 URL을 찾아 반환하는 유틸리티
"""

import json
from pathlib import Path
from typing import Optional

# =====================================================
# 상수: 카테고리 데이터 파일 경로
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CATEGORY_JSON_PATH = PROJECT_ROOT / "storage" / "category_structure.json"

# =====================================================
# 함수
# =====================================================
def resolve_category_url(mid_key: str, detail_key: str) -> Optional[str]:
    """
    주어진 중간키와 세부항목 쌍에 해당하는 URL을 반환합니다.
    없으면 None을 반환합니다.

    Args:
        mid_key (str): 중간 카테고리 이름
        detail_key (str): 세부 카테고리 이름

    Returns:
        str | None: 해당 카테고리의 URL
    """
    if not CATEGORY_JSON_PATH.exists():
        print(f"⚠️ 카테고리 데이터 파일이 존재하지 않습니다: {CATEGORY_JSON_PATH}")
        return None

    try:
        with open(CATEGORY_JSON_PATH, "r", encoding="utf-8") as f:
            category_data = json.load(f)
    except Exception as e:
        print(f"❌ 카테고리 데이터 로드 실패: {e}")
        return None

    # top_name → mid_name → [(detail_name, url), …]
    for top_name, mid_dict in category_data.items():
        if mid_key not in mid_dict:
            continue

        for detail_name, url in mid_dict[mid_key]:
            if detail_name == detail_key:
                return url

    print(f"⚠️ ({mid_key}, {detail_key})에 해당하는 URL을 찾을 수 없습니다.")
    return None


# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    mid = "자동차용품"
    detail = "세차/와이퍼/방향제"

    url = resolve_category_url(mid, detail)
    if url:
        print(f"✅ URL: {url}")
    else:
        print("❌ URL을 찾을 수 없습니다.")
