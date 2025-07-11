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
from pathlib import Path
from app.utils.category_spec_storage import save_category_spec
from fastapi import BackgroundTasks
from chatbot_llm.is_affirmative_llm import is_affirmative
from app.utils.category_spec_storage import save_category_spec, load_category_spec, sanitize_filename

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
    detail_key = bot_data.get("detail_key")  # 원본
    url = bot_data.get("url")

    # 🔷 LLM으로 긍정/부정 판단
    affirmative = await is_affirmative(utterance)

    if not affirmative:
        update_session(user_id, stage=1, user_utterance=utterance)
        return "✅ 이전 단계로 돌아갑니다. 원하시는 상품을 다시 말씀해 주세요!"

    # 🔷 파일 존재 여부 확인
    sanitized_key = sanitize_filename(detail_key)
    file_path = f"storage/category_spec/{sanitized_key}.json"

    if Path(file_path).exists():
        # 파일이 있으면 로드 (load_category_spec 내부에서 sanitize 처리됨)
        cached = load_category_spec(detail_key)
        crawled_data = cached["data"]
    else:
        # 파일 없으면 크롤링 (원본 detail_key 사용)
        crawl_result = await execute_category_crawling(detail_key, url)

        if not crawl_result or (isinstance(crawl_result, list) and not crawl_result[0]):
            update_session(user_id, stage=1, user_utterance=utterance)
            return crawl_result[1] if isinstance(crawl_result, list) and len(crawl_result) > 1 \
                else "죄송합니다. 크롤링에 실패했습니다. 다시 시도해 주세요."

        crawled_data = crawl_result[1]

        # 💾 저장을 비동기적으로 진행 (원본 detail_key 사용)
        background_tasks.add_task(save_category_spec, url, detail_key, crawled_data)

    # 세션 갱신
    update_session(user_id, stage=4, user_utterance=utterance, bot_raw_result=crawled_data)

    return format_crawled_result(crawled_data)


# =======================================================
# Stage 4 상태 유틸
# =======================================================
def get_stage4_state(session: dict) -> dict:
    return session.get("stage4_state", {})


def update_stage4_state(user_id: str, **kwargs):
    session = get_session(user_id)
    state = session.get("stage4_state", {})
    state.update(kwargs)
    update_session(user_id, stage4_state=state)

# =======================================================
# Stage 4 핸들러
# =======================================================
async def handle_stage_4(user_id: str, utterance: str, background_tasks) -> str:
    session = get_session(user_id)
    crawled_data = session.get("last_bot_message", {})  # Stage 3 결과

    stage4_state = get_stage4_state(session)

    # 현재 단계가 두 번째 선택 단계인지 확인
    if stage4_state.get("first_selection") and not stage4_state.get("second_selection"):
        # 두 번째 선택 단계
        second_key = stage4_state.get("second_key")
        second_choices = crawled_data.get(second_key, [])
        print(second_key , second_choices)
        # 유효성 확인
        from chatbot_llm.is_valid_choice_llm import is_valid_choice
        result = await is_valid_choice(utterance, {second_key: second_choices})

        if not result["valid"]:
            print("설마 여기?")
            update_session(user_id, stage=1, user_utterance=utterance)
            return "✅ 선택을 다시 진행할게요. 원하시는 상품을 다시 말씀해 주세요!"

        # 유효 → 확인 질문
        matched = ", ".join(result["matched_choices"])
        update_stage4_state(user_id, second_selection=result["matched_choices"])

        return (
            f"방금 선택하신 {second_key} ‘{matched}’로 진행할까요? "
            f"진행을 원하시면 긍정의 의사를 알려주세요."
        )
    print("두번째 접근")
    # 두 번째 선택 확인 긍/부 답변
    if stage4_state.get("first_selection") and not stage4_state.get("second_selection"):
        from chatbot_llm.is_affirmative_llm import is_affirmative
        affirmative = await is_affirmative(utterance)

        if affirmative:
            # 유저가 긍정 → 두 번째 선택으로 진행
            second_key = stage4_state.get("second_key")
            second_choices = crawled_data.get(second_key, [])
            choices_str = "\n".join(f"- {item}" for item in second_choices)
            return f"다음 중 하나를 선택해 주세요. 가능한 {second_key}는 다음과 같습니다:\n{choices_str}"

        else:
            # 유저가 부정 → 다시 첫 번째 선택부터
            print("여기인가?")
            update_session(user_id, stage=1, user_utterance=utterance)
            return "✅ 선택을 다시 진행할게요. 원하시는 상품을 다시 말씀해 주세요!"

    # 첫 번째 선택 단계
    first_key = list(crawled_data.keys())[0]
    first_choices = crawled_data[first_key]

    # 유효성 확인
    from chatbot_llm.is_valid_choice_llm import is_valid_choice
    result = await is_valid_choice(utterance, {first_key: first_choices})

    if not result["valid"]:
        print("이쪽인가?")
        update_session(user_id, stage=1, user_utterance=utterance)
        return "✅ 선택을 다시 진행할게요. 원하시는 상품을 다시 말씀해 주세요!"

    # 유효 → 확인 질문
    matched = ", ".join(result["matched_choices"])
    update_stage4_state(user_id, first_key=first_key, first_selection=result["matched_choices"])

    return (
        f"방금 선택하신 {first_key} ‘{matched}’로 진행할까요? "
        f"진행을 원하시면 긍정의 의사를 알려주세요."
    )




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
    elif stage == 4:
        response_text = await handle_stage_4(user_id, utterance, background_tasks)
    else:
        update_session(user_id, stage=stage, user_utterance=utterance)
        response_text = "작업을 계속 진행합니다…"

    return make_kakao_response(response_text)
