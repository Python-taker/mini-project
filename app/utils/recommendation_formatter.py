"""
recommendation_formatter.py
──────────────────────────────
- 추천 결과 dict를 보기 좋은 문자열로 포맷팅
"""

def format_recommendation_message(
    header_text: str,
    recommended: dict[str, list[str]],
    footer_text: str = ""
) -> str:
    """
    추천 결과를 보기 좋은 문자열로 반환합니다.

    Args:
        header_text (str): 결과 위쪽에 표시할 문구
        recommended (dict): 추천 결과 {중간키: [세부항목, …]}
        footer_text (str): 결과 아래쪽에 표시할 문구

    Returns:
        str: 사용자에게 보여줄 최종 메시지
    """
    lines = [header_text.strip()]
    idx = 1

    for mid_key, details in recommended.items():
        lines.append(f"=====  🔷 {mid_key} 🔷  =====")
        for detail in details:
            lines.append(f"{idx}. {detail}")
            idx += 1
        lines.append("")  # 키 구분용 빈 줄

    if footer_text.strip():
        lines.append(footer_text.strip())

    return "\n".join(lines)

# 다른 키가 여러 개여도 첫 번째 키만 출력하도록 의도적으로 작성함
def format_crawled_result(result: dict) -> str:
    """
    크롤링 결과를 사용자 메시지용 문자열로 변환

    Args:
        result (dict): 크롤링 결과 딕셔너리

    Returns:
        str: 포맷팅된 메시지 문자열
    """
    if not result or not isinstance(result, dict):
        return "죄송합니다. 추천할 정보를 찾지 못했습니다."

    # nav를 제외한 다른 키가 있는지 검사
    other_keys = [k for k in result.keys() if k != "nav"]

    if other_keys:
        # 다른 키가 하나라도 있으면 그 키의 리스트를 출력
        mid_key = other_keys[0]
        details = result.get(mid_key, [])
        if isinstance(details, list) and details:
            lines = [f"=====  ⭐️ {mid_key} ⭐️  ====="]
            for idx, detail in enumerate(details, start=1):
                lines.append(f"{idx}. {detail}")
            lines.append("")
            lines.append("원하시는 추천 항목 번호를 모두 입력해 주세요!")
            return "\n".join(lines)

    # 다른 키가 없고 nav만 있을 때
    nav = result.get("nav", {})
    if nav:
        lines = [f"=====  🔶 유사 항목 🔶  ====="]
        for idx, (name, _) in enumerate(nav.items(), start=1):
            lines.append(f"{idx}. {name}")
        lines.append("")
        lines.append("원하시는 유사 항목 번호를 입력해 주세요!")
        return "\n".join(lines)

    return "죄송합니다. 추천할 정보를 찾지 못했습니다."