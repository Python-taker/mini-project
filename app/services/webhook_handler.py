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
from app.utils.recommendation_formatter import format_recommendation_message
from app.utils.session_manager import (
    get_session,
    update_session,
    clear_session
)


async def handle_webhook(data: dict) -> dict:
    """
    카카오톡 webhook 요청을 처리하고 응답 payload를 생성합니다.
    """
    user_id = extract_user_id(data)
    utterance = extract_utterance(data)

    token_info = get_user_token(user_id)

    if not token_info:
        # 🔷 인증 필요
        auth_url = build_kakao_auth_url(user_id)
        response_text = (
            "🔐 인증이 필요합니다. 처음 방문하셨군요!\n"
            f"[여기서 인증하기]({auth_url})"
        )

    elif token_info.get("failed", False):
        # 🔷 인증 실패
        auth_url = build_kakao_auth_url(user_id)
        response_text = (
            "❌ 이전 인증이 실패했습니다. 다시 시도해 주세요!\n"
            f"[여기서 인증하기]({auth_url})"
        )

    elif is_token_expired(user_id):
        # 🔷 인증 만료
        auth_url = build_kakao_auth_url(user_id)
        response_text = (
            "⏳ 인증이 만료되었습니다. 다시 인증해 주세요.\n"
            f"[여기서 재인증하기]({auth_url})"
        )

    elif token_info.get("just_authenticated", False):
        # 🔷 인증 직후
        response_text = (
            "✅ 인증이 완료되었습니다. 카테고리를 추천해 드리겠습니다. 원하는 상품을 말씀해 주세요~!"
        )
        clear_just_authenticated(user_id)
        clear_session(user_id)  # 기존 세션 초기화
        update_session(user_id, stage=1, user_utterance=utterance)

    else:
        # 🔷 평소 대화
        session = get_session(user_id)
        stage = session["stage"]

        if stage == 1:
            # 🔷 추천 서비스 호출
            result = await recommend_category(utterance)
            if result[0]:
                # 추천 성공 → 포맷팅
                response_text = format_recommendation_message(
                    "추천 결과입니다:",
                    result[1],
                    "원하시는 항목 번호를 입력해 주세요!"
                )
                update_session(user_id, stage=2, user_utterance=utterance, bot_raw_result=result[1])
            else:
                # 추천 실패
                response_text = result[1]
                update_session(user_id, stage=1, user_utterance=utterance)

        elif stage == 2:
            response_text = "선택하신 카테고리의 제조사를 알려주세요."
            update_session(user_id, stage=3, user_utterance=utterance)

        elif stage == 3:
            response_text = "선택하신 제조사의 브랜드를 알려주세요."
            update_session(user_id, stage=4, user_utterance=utterance)

        else:
            response_text = "작업을 계속 진행합니다…"
            update_session(user_id, stage=stage, user_utterance=utterance)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }
