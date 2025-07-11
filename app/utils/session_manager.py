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
    stage: Optional[int] = None,
    user_utterance: Optional[str] = None,
    bot_raw_result: Optional[dict] = None,
    **kwargs
) -> None:
    """
    세션 상태 업데이트

    Args:
        user_id (str): 유저 고유 ID
        stage (int, optional): 현재 단계
        user_utterance (str, optional): 사용자가 입력한 문장
        bot_raw_result (dict | None, optional): 챗봇 추천 결과(raw)
        **kwargs: 기타 세션에 저장할 추가 키-값
    """
    session = get_session(user_id)

    if stage is not None:
        session["stage"] = stage
    if user_utterance is not None:
        session["last_user_input"] = user_utterance
    if bot_raw_result is not None:
        session["last_bot_message"] = bot_raw_result

    # 기타 키-값 업데이트
    for k, v in kwargs.items():
        session[k] = v

    # history 누적
    if user_utterance is not None:
        session["history"].append({
            "user": user_utterance,
            "bot_raw": bot_raw_result
        })


def clear_session(user_id: str) -> None:
    """
    유저 세션을 삭제합니다.
    """
    session_states.pop(user_id, None)
