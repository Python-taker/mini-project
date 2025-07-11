"""
build_category_dict.py
──────────────────────────────
- validate_llm 결과를 기반으로 category_structure_keys.json 에서 세부 항목 딕셔너리 생성
"""

import json
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]

CATEGORY_KEYS_JSON = get_project_root() / "storage" / "category_structure_keys.json"

# =====================================================
# 유틸 함수: JSON 로드
# =====================================================
def load_category_keys() -> dict:
    with open(CATEGORY_KEYS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

# =====================================================
# 메인 함수
# =====================================================
def build_category_dict(selected_keywords: list, category_keys: dict | None = None) -> dict[str, list[str]]:
    """
    선택된 키워드를 기반으로 세부 항목 딕셔너리 생성

    Args:
        selected_keywords: [True, "키1", "키2", …]
        category_keys: category_structure_keys.json 을 딕셔너리로 로드한 값 (없으면 자동 로드)

    Returns:
        dict: {중간키: [하위항목, …]}
    """
    if not selected_keywords or not isinstance(selected_keywords, list) or selected_keywords[0] is not True:
        raise ValueError("첫 번째 요소가 True인 키워드 리스트가 필요합니다.")

    if category_keys is None:
        category_keys = load_category_keys()

    result = {}
    seen_keys = set()

    for keyword in selected_keywords[1:]:
        # 최상위 키워드
        if keyword in category_keys:
            for mid_key, items in category_keys[keyword].items():
                if mid_key not in seen_keys:
                    result[mid_key] = items
                    seen_keys.add(mid_key)

        # 중간 키워드
        else:
            for top_key, mids in category_keys.items():
                if keyword in mids:
                    if keyword not in seen_keys:
                        result[keyword] = mids[keyword]
                        seen_keys.add(keyword)

    return result

# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    # 예시 입력
    example_input = [True, "키보드/마우스/웹캠", "컴퓨터 · 노트북 · 조립PC"]

    print(f"입력: {example_input}")
    output = build_category_dict(example_input)
    print("\n출력:")
    print(json.dumps(output, ensure_ascii=False, indent=2))
