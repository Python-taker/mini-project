def extract_utterance(data: dict) -> str:
    """
    카카오톡 webhook 요청 데이터에서 사용자 발화(utterance)를 추출합니다.
    """
    try:
        return data["userRequest"]["utterance"]
    except (KeyError, TypeError):
        return ""


def extract_intent(data: dict) -> str:
    """
    카카오톡 webhook 요청 데이터에서 사용자가 매칭된 intent 이름을 추출합니다.
    """
    try:
        return data["intent"]["name"]
    except (KeyError, TypeError):
        return ""


def extract_user_id(data: dict) -> str:
    """
    카카오톡 webhook 요청 데이터에서 사용자 고유 ID를 추출합니다.
    """
    try:
        return data["userRequest"]["user"]["id"]
    except (KeyError, TypeError):
        return ""


def extract_block_name(data: dict) -> str:
    """
    카카오톡 webhook 요청 데이터에서 현재 블록 이름을 추출합니다.
    """
    try:
        return data["userRequest"]["block"]["name"]
    except (KeyError, TypeError):
        return ""


def extract_params(data: dict) -> dict:
    """
    카카오톡 webhook 요청 데이터에서 액션의 params를 딕셔너리 형태로 추출합니다.
    """
    try:
        return data["action"].get("params", {})
    except (KeyError, TypeError):
        return {}
