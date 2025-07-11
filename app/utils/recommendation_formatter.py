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
