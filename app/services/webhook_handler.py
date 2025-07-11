"""
webhook_handler.py
──────────────────────────────
- 카카오톡 webhook 요청 처리
- 인증 상태 관리 & 단계별 대화 처리
"""

from app.utils.parser import extract_utterance, extract_user_id
from storage.token_manager import (
    get_user_token,
    is_token_expired,
    clear_just_authenticated
)
from app.utils.kakao_oauth import build_kakao_auth_url
from app.services.category_recommendation_service import recommend_category
from app.services.category_flow_executor import (
    prepare_category_flow,
    execute_category_crawling
)
from app.utils.recommendation_formatter import (
    format_recommendation_message,
    format_crawled_result
)
from app.utils.session_manager import (
    get_session,
    update_session,
    clear_session
)
from app.utils.category_spec_storage import save_category_spec
from fastapi import BackgroundTasks
from chatbot_llm.is_affirmative_llm import is_affirmative

# =======================================================
# 공통 응답 생성
# =======================================================
def make_kakao_response(text: str) -> dict:
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ]
        }
    }


# =======================================================
# 인증 상태 처리
# =======================================================
def handle_auth_state(user_id: str, utterance: str, token_info: dict) -> str:
    if not token_info:
        auth_url = build_kakao_auth_url(user_id)
        return f"🔐 인증이 필요합니다. 처음 방문하셨군요!\n[여기서 인증하기]({auth_url})"
    if token_info.get("failed", False):
        auth_url = build_kakao_auth_url(user_id)
        return f"❌ 이전 인증이 실패했습니다. 다시 시도해 주세요!\n[여기서 인증하기]({auth_url})"
    if is_token_expired(user_id):
        auth_url = build_kakao_auth_url(user_id)
        return f"⏳ 인증이 만료되었습니다. 다시 인증해 주세요.\n[여기서 재인증하기]({auth_url})"
    if token_info.get("just_authenticated", False):
        clear_just_authenticated(user_id)
        clear_session(user_id)
        update_session(user_id, stage=1, user_utterance=utterance)
        return "✅ 인증이 완료되었습니다. 카테고리를 추천해 드리겠습니다. 원하는 상품을 말씀해 주세요~!"
    return None  # 인증 정상


# =======================================================
# stage 1 핸들러
# =======================================================
async def handle_stage_1(user_id: str, utterance: str) -> str:
    result = await recommend_category(utterance)
    if result[0]:
        response_text = format_recommendation_message(
            "추천 결과입니다:",
            result[1],
            "원하시는 항목 번호를 입력해 주세요!"
        )
        update_session(user_id, stage=2, user_utterance=utterance, bot_raw_result=result[1])
    else:
        response_text = result[1]
        update_session(user_id, stage=1, user_utterance=utterance)
    return response_text


# =======================================================
# stage 2 핸들러
# =======================================================
async def handle_stage_2(user_id: str, utterance: str) -> str:
    flow_result = await prepare_category_flow(user_id, utterance)

    if not flow_result or (isinstance(flow_result, list) and not flow_result[0]):
        return flow_result[1] if isinstance(flow_result, list) and len(flow_result) > 1 \
            else "죄송합니다. 요청하신 작업을 처리하지 못했습니다. 다시 시도해 주세요."

    mid_key, detail_key, url = flow_result[1]
    update_session(user_id, stage=3, user_utterance=utterance, bot_raw_result={
        "mid_key": mid_key,
        "detail_key": detail_key,
        "url": url
    })

    return (
        f"🔍 선택하신 항목은 다음과 같습니다:\n"
        f"• 카테고리: {mid_key}\n"
        f"• 세부 항목: {detail_key}\n\n"
        f"이 항목으로 진행할까요? 진행을 원하시면 긍정의 의사를 알려주세요."
    )


# =======================================================
# stage 3 핸들러
# =======================================================
async def handle_stage_3(user_id: str, utterance: str, background_tasks) -> str:
    session = get_session(user_id)
    bot_data = session.get("last_bot_message", {})
    detail_key = bot_data.get("detail_key")
    url = bot_data.get("url")

    # 🔷 LLM으로 긍정/부정 판단
    affirmative = await is_affirmative(utterance)

    if not affirmative:
        update_session(user_id, stage=1, user_utterance=utterance)
        return "✅ 이전 단계로 돌아갑니다. 원하시는 상품을 다시 말씀해 주세요!"

    crawl_result = execute_category_crawling(detail_key, url)

    if not crawl_result or (isinstance(crawl_result, list) and not crawl_result[0]):
        return crawl_result[1] if isinstance(crawl_result, list) and len(crawl_result) > 1 \
            else "죄송합니다. 크롤링에 실패했습니다. 다시 시도해 주세요."

    crawled_data = crawl_result[1]

    # 💾 저장을 비동기적으로 진행
    background_tasks.add_task(save_category_spec, url, detail_key, crawled_data)

    update_session(user_id, stage=4, user_utterance=utterance)

    return format_crawled_result(crawled_data)


# =======================================================
# 메인 핸들러
# =======================================================
async def handle_webhook(data: dict, background_tasks: BackgroundTasks) -> dict:
    user_id = extract_user_id(data)
    utterance = extract_utterance(data)

    token_info = get_user_token(user_id)
    auth_message = handle_auth_state(user_id, utterance, token_info)
    if auth_message:
        return make_kakao_response(auth_message)

    session = get_session(user_id)
    stage = session.get("stage", 1)

    if stage == 1:
        response_text = await handle_stage_1(user_id, utterance)
    elif stage == 2:
        response_text = await handle_stage_2(user_id, utterance)
    elif stage == 3:
        response_text = await handle_stage_3(user_id, utterance, background_tasks)
    else:
        update_session(user_id, stage=stage, user_utterance=utterance)
        response_text = "작업을 계속 진행합니다…"

    return make_kakao_response(response_text)
