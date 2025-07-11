"""
category_flow_executor.py
──────────────────────────────
- 유저 입력과 세션 데이터를 기반으로
  카테고리 매칭 → URL 해석 → (확인 후) 크롤링까지 수행
  (저장은 호출하는 쪽에서 처리)
"""

import asyncio
from app.utils.session_manager import get_session
from app.utils.category_url_resolver import resolve_category_url
from chatbot_llm.category_match_llm import category_match
from selenium_utils.manufacturer_brand_crawler import crawl_spec_options

async def prepare_category_flow(user_id: str, utterance: str):
    """
    카테고리 매칭 → URL 해석까지만 수행
    (사용자 확인 후 크롤링 단계 진행)

    Args:
        user_id (str): 유저 ID
        utterance (str): 사용자 입력

    Returns:
        [bool, list | str]: 성공 시 [True, (mid_key, detail_key, url)], 실패 시 [False, 메시지]
    """
    bot_raw_result = get_session(user_id).get("last_bot_message")

    llm_result = await category_match(utterance, bot_raw_result)
    if not llm_result or not llm_result[0]:  # 실패
        return llm_result

    mid_key, detail_key = llm_result[1]

    url = resolve_category_url(mid_key, detail_key)
    if not url:
        return [False, "죄송합니다. 카테고리 URL을 찾지 못했습니다."]

    # 확인용 데이터 반환
    return [True, (mid_key, detail_key, url)]


async def execute_category_crawling(detail_key: str, url: str):
    """
    URL에 대해 크롤링만 수행
    (저장은 호출하는 쪽에서 처리)

    Args:
        detail_key (str): 세부 항목 키
        url (str): 크롤링할 URL

    Returns:
        [bool, dict | str]: 성공 시 [True, 크롤링 데이터], 실패 시 [False, 메시지]
    """
    # 크롤링은 블로킹 동작이므로 별도 스레드로 실행
    crawled_data = await asyncio.to_thread(crawl_spec_options, url)

    if not crawled_data or all(len(v) == 0 for v in crawled_data.values()):
        return [False, "죄송합니다. 카테고리 정보를 가져오지 못했습니다."]

    return [True, crawled_data]


# =======================================================
# CLI 테스트
# =======================================================
if __name__ == "__main__":
    import asyncio
    from app.utils.session_manager import update_session
    from app.utils.category_spec_storage import save_category_spec

    TEST_USER_ID = "test_user_123"
    TEST_UTTERANCE = "세차 용품"

    # 세션 mock 데이터 준비
    mock_bot_raw_result = {
        "자동차용품": ["오일/첨가제/필터", "세차/와이퍼/방향제", "부품/외장/안전"],
        "부품/외장/안전": ["브레이크패드", "점화플러그/부품"]
    }
    update_session(TEST_USER_ID, stage=3, user_utterance=TEST_UTTERANCE, bot_raw_result=mock_bot_raw_result)

    print(f"🧪 테스트: utterance='{TEST_UTTERANCE}'")

    llm_url_result = asyncio.run(prepare_category_flow(TEST_USER_ID, TEST_UTTERANCE))
    if not llm_url_result[0]:
        print(f"❌ 실패: {llm_url_result[1]}")
    else:
        mid_key, detail_key, url = llm_url_result[1]
        print(f"✅ 매칭 완료: {mid_key} > {detail_key}")
        print(f"URL: {url}")
        print("크롤링을 진행합니다…")

        crawl_result = asyncio.run(execute_category_crawling(detail_key, url))
        if crawl_result[0]:
            print(f"✅ 크롤링 성공")
            crawled_data = crawl_result[1]
            for k, v in crawled_data.items():
                if isinstance(v, list):
                    print(f"- {k}: {', '.join(v)}")
                elif isinstance(v, dict):
                    print(f"- {k}:")
                    for txt, link in v.items():
                        print(f"  • {txt}: {link}")

            # 저장은 호출하는 쪽에서
            save_category_spec(url, detail_key, crawled_data)

        else:
            print(f"❌ 크롤링 실패: {crawl_result[1]}")
