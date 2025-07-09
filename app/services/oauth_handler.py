from app.utils.kakao_oauth import get_kakao_access_token
from storage.token_manager import save_user_token


def handle_oauth(params: dict) -> dict:
    """
    카카오 OAuth 콜백 처리
    """
    code = params.get("code")
    state = params.get("state")  # webhook에서 전달한 user_id가 여기에 담겨옴

    if not code or not state:
        return {"error": "code 또는 state가 없습니다."}

    token_info = get_kakao_access_token(code)

    save_user_token(
        user_id=state,
        access_token=token_info["access_token"],
        refresh_token=token_info["refresh_token"],
        expires_in=token_info["expires_in"]
    )

    return {
        "message": "인증 및 토큰 저장 완료",
        "token_info": token_info
    }
