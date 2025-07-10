import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKENS_FILE = Path(__file__).resolve().parent / "tokens.json"
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
BASE_URL = os.getenv("BASE_URL") or ""


def load_tokens() -> dict:
    if TOKENS_FILE.exists():
        with open(TOKENS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_tokens(tokens: dict):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)


def save_failed_state(user_id: str):
    tokens = load_tokens()
    tokens[user_id] = {
        "failed": True
    }
    save_tokens(tokens)


def save_user_token(user_id: str, access_token: str, refresh_token: str, expires_in: int):
    tokens = load_tokens()
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
    tokens[user_id] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "failed": False,                # 인증 성공 시 failed 상태 해제
        "just_authenticated": True     # 인증 직후 1회 메시지 표시
    }
    save_tokens(tokens)


def get_user_token(user_id: str) -> dict:
    tokens = load_tokens()
    return tokens.get(user_id)


def clear_just_authenticated(user_id: str):
    tokens = load_tokens()
    if user_id in tokens and tokens[user_id].get("just_authenticated"):
        tokens[user_id]["just_authenticated"] = False
        save_tokens(tokens)


def is_token_expired(user_id: str) -> bool:
    user_token = get_user_token(user_id)
    if not user_token or "expires_at" not in user_token:
        return True
    try:
        expires_at = datetime.fromisoformat(user_token["expires_at"])
    except ValueError:
        return True
    return datetime.now(timezone.utc) >= expires_at


def refresh_access_token(user_id: str) -> dict:
    """
    refresh_token을 이용해 새로운 access_token을 발급하고 저장.
    """
    user_token = get_user_token(user_id)
    if not user_token or "refresh_token" not in user_token:
        raise ValueError(f"User {user_id} has no refresh_token.")

    url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_API_KEY,
        "refresh_token": user_token["refresh_token"]
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    result = response.json()

    # 갱신된 값 저장
    access_token = result["access_token"]
    expires_in = result.get("expires_in", 21599)  # 보통 6시간
    refresh_token = result.get("refresh_token", user_token["refresh_token"])  # 새 refresh_token이 있으면 갱신

    save_user_token(user_id, access_token, refresh_token, expires_in)

    return {
        "access_token": access_token,
        "expires_in": expires_in,
        "refresh_token": refresh_token
    }
