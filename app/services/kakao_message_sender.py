import json
import requests
from storage.token_manager import get_user_token
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "")

def send_kakao_message(user_id: str, text: str):
    """
    카카오톡으로 사용자에게 메시지를 보냄
    """
    token_info = get_user_token(user_id)
    if not token_info:
        print(f"⚠️ {user_id} 토큰 없음. 메시지 못보냄.")
        return

    access_token = token_info["access_token"]
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": BASE_URL,
                "mobile_web_url": BASE_URL
            }
        })
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.ok:
        print(f"✅ 카톡 메시지 전송 완료: {user_id}")
    else:
        print(f"❌ 메시지 전송 실패: {response.text}")
