from app.utils.kakao_oauth import get_kakao_access_token
from storage.token_manager import save_user_token, save_failed_state

def handle_oauth(params: dict) -> dict:
    """
    카카오 OAuth 콜백 처리
    - params: redirect_uri로 전달된 쿼리 파라미터 (code, state)
    - state: OAuth 요청 시 넘긴 user_id가 그대로 전달됨
    """
    code = params.get("code")
    user_id = params.get("state")  # state에 user_id가 담겨옴

    if not code or not user_id:
        return {"error": "code 또는 user_id(state)가 없습니다."}

    try:
        token_info = get_kakao_access_token(code)
    except Exception as e:
        save_failed_state(user_id)
        return {"error": str(e)}

    save_user_token(
        user_id=user_id,
        access_token=token_info["access_token"],
        refresh_token=token_info["refresh_token"],
        expires_in=token_info["expires_in"]
    )

    return {
        "message": f"사용자({user_id}) 인증 및 토큰 저장 완료",
        "token_info": token_info
    }
