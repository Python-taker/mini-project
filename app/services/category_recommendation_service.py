"""
category_recommendation_service.py
──────────────────────────────
- 사용자 입력 → validate_llm → build_category_dict → refine_llm
- 카테고리 추천 서비스 전체 워크플로 처리
"""

from chatbot_llm.validate_llm import validate_keywords
from chatbot_llm.refine_llm import refine_keywords
from app.utils.build_category_dict import build_category_dict


async def recommend_category(user_message: str) -> list:
    """
    사용자 입력을 받아 카테고리 추천 결과를 리턴합니다.

    Args:
        user_message (str): 사용자의 발화

    Returns:
        list: [True, {...}] 또는 [False, "안내 문구"]
    """
    # 1️⃣ validate 단계
    validate_result = await validate_keywords(user_message)

    if not validate_result or validate_result[0] is not True:
        # validate 실패
        return validate_result

    # 2️⃣ build_category_dict 단계
    try:
        category_dict = build_category_dict(validate_result)
    except Exception as e:
        print(f"❌ build_category_dict 실패: {e}")
        return [False, "죄송합니다. 카테고리 데이터를 처리하는 중 오류가 발생했습니다. 다시 시도해 주세요."]

    if not category_dict:
        return [False, "죄송합니다. 적합한 카테고리를 찾지 못했습니다. 다시 시도해 주세요."]

    # 3️⃣ refine 단계
    refine_result = await refine_keywords(user_message, category_dict)

    if not refine_result or refine_result[0] is not True:
        # refine 실패
        return refine_result

    # 최종 결과
    return refine_result



# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    import asyncio
    example_input = "사무실에서 쓸 만한 노트북 추천해줘"
    print(f"입력: {example_input}")
    result = asyncio.run(recommend_category(example_input))
    print("출력:")
    from pprint import pprint
    pprint(result)
