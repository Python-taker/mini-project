import os
import requests

from dotenv import load_dotenv
from app.utils.config import BASE_URL

# 환경 변수 로드
load_dotenv()
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")


def build_kakao_auth_url(user_id: str = "") -> str:
    """
    카카오 로그인 인증 URL 생성
    - user_id를 state 파라미터로 전달
    """
    redirect_uri = f"{BASE_URL}/oauth"
    url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    if user_id:
        url += f"&state={user_id}"
    return url


def get_kakao_access_token(code: str) -> dict:
    """
    카카오 access_token 발급
    - 인자로 전달받은 일회성 code를 이용해 토큰 발급 요청
    """
    redirect_uri = f"{BASE_URL}/oauth"
    url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()
