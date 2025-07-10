from storage.token_manager import get_user_token, is_token_expired
from app.utils.kakao_oauth import build_kakao_auth_url

def check_user_auth(user_id: str) -> tuple[bool, str]:
    """
    user_id에 대한 인증 상태를 확인
    - 인증 유효하면: (True, None)
    - 인증 필요하면: (False, auth_url)
    """
    token = get_user_token(user_id)
    if not token or is_token_expired(user_id):
        auth_url = build_kakao_auth_url(user_id)
        return False, auth_url
    return True, None
