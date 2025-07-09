import os
import requests

from dotenv import load_dotenv
from utils.config import BASE_URL
from utils.parser import extract_user_id
from storage.token_manager import save_user_token

# 환경 변수 로드
load_dotenv()
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")


def build_kakao_auth_url() -> str:
    """
    카카오 로그인 인증 URL 생성
    - BASE_URL에 /oauth를 붙여 redirect_uri로 사용
    """
    redirect_uri = f"{BASE_URL}/oauth"
    url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
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


def handle_oauth_callback(data: dict, code: str) -> dict:
    """
    카카오 OAuth 콜백 처리 및 사용자 토큰 저장
    - data: 카카오 webhook 데이터 (user_id 추출에 사용)
    - code: 카카오가 리디렉션 시 넘겨준 일회성 인증 코드
    """
    user_id = extract_user_id(data)
    token_info = get_kakao_access_token(code)

    save_user_token(
        user_id=user_id,
        access_token=token_info["access_token"],
        refresh_token=token_info["refresh_token"],
        expires_in=token_info["expires_in"]
    )

    return token_info
