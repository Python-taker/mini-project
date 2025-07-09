from fastapi import FastAPI, Request

### ========== local library ========== ###
from app.services.webhook_handler import handle_webhook
from app.services.oauth_handler import handle_oauth
from app.utils.kakao_oauth import build_kakao_auth_url

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "FastAPI 챗봇 서버 실행 중!"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    return handle_webhook(data)


@app.get("/auth_url")
async def auth_url():
    """
    인증 URL 확인용 엔드포인트
    """
    url = build_kakao_auth_url()
    return {"auth_url": url}


@app.get("/oauth")
async def oauth(request: Request):
    """
    카카오 OAuth 인증 콜백 엔드포인트
    """
    params = dict(request.query_params)
    return handle_oauth(params)
