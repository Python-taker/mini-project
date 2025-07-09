import json
from pathlib import Path
from datetime import datetime, timedelta

TOKENS_FILE = Path(__file__).resolve().parent / "tokens.json"


def load_tokens() -> dict:
    if TOKENS_FILE.exists():
        with open(TOKENS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_tokens(tokens: dict):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)


def save_user_token(user_id: str, access_token: str, refresh_token: str, expires_in: int):
    tokens = load_tokens()
    expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
    tokens[user_id] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }
    save_tokens(tokens)


def get_user_token(user_id: str) -> dict:
    tokens = load_tokens()
    return tokens.get(user_id)
