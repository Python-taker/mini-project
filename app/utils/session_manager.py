"""
session_manager.py
──────────────────────────────
- 유저별 세션 상태 관리
"""

from typing import Optional

# 전역 세션 상태 저장소
session_states: dict[str, dict] = {}

def get_session(user_id: str) -> dict:
    """
    유저 세션을 가져오거나 초기화합니다.
    """
    return session_states.setdefault(user_id, {
        "stage": 1,
        "history": [],
        "last_user_input": None,
        "last_bot_message": None,
        "just_authenticated": False
    })


def update_session(
    user_id: str,
    stage: int,
    user_utterance: str,
    bot_raw_result: Optional[dict] = None
) -> None:
    """
    세션 상태(stage, history) 업데이트

    Args:
        user_id (str): 유저 고유 ID
        stage (int): 현재 단계
        user_utterance (str): 사용자가 입력한 문장
        bot_raw_result (dict | None): 챗봇 추천 결과(raw)
    """
    session = get_session(user_id)
    session["stage"] = stage
    session["last_user_input"] = user_utterance
    session["last_bot_message"] = bot_raw_result  # 최근 응답 저장

    # history 누적
    session["history"].append({
        "user": user_utterance,
        "bot_raw": bot_raw_result
    })


def clear_session(user_id: str) -> None:
    """
    유저 세션을 삭제합니다.
    """
    session_states.pop(user_id, None)
