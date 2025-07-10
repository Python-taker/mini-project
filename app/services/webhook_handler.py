from app.utils.parser import extract_utterance, extract_user_id
from storage.token_manager import (
    get_user_token,
    is_token_expired,
    clear_just_authenticated
)
from app.utils.kakao_oauth import build_kakao_auth_url


def handle_webhook(data: dict) -> dict:
    user_id = extract_user_id(data)
    utterance = extract_utterance(data)

    token_info = get_user_token(user_id)

    if not token_info:
        auth_url = build_kakao_auth_url(user_id)
        response_text = (
            "🔐 인증이 필요합니다. 처음 방문하셨군요!\n"
            f"[여기서 인증하기]({auth_url})"
        )
    elif token_info.get("failed", False):
        auth_url = build_kakao_auth_url(user_id)
        response_text = (
            "❌ 이전 인증이 실패했습니다. 다시 시도해 주세요!\n"
            f"[여기서 인증하기]({auth_url})"
        )
    elif is_token_expired(user_id):
        auth_url = build_kakao_auth_url(user_id)
        response_text = (
            "⏳ 인증이 만료되었습니다. 다시 인증해 주세요.\n"
            f"[여기서 재인증하기]({auth_url})"
        )
    elif token_info.get("just_authenticated", False):
        # 인증 직후 1회만 메시지
        response_text = "✅ 인증이 완료되었습니다. 무엇을 도와드릴까요?"
        clear_just_authenticated(user_id)
    else:
        # 평소 대화
        response_text = "무엇을 도와드릴까요?"

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
