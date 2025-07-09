from app.utils.parser import extract_utterance
from app.utils.kakao_oauth import build_kakao_auth_url


def handle_webhook(data: dict) -> dict:
    """
    웹훅 데이터 처리
    """
    print(f"📩 받은 데이터: {data}")
    utterance = extract_utterance(data)

    # 예시: 인증 URL 안내
    auth_url = build_kakao_auth_url(state=extract_utterance(data))

    response_text = f"받은 메시지: {utterance}\n\n[여기서 인증하기]({auth_url})"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }
