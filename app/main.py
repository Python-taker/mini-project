from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.webhook_handler import handle_webhook
from app.services.oauth_handler import handle_oauth
from app.utils.kakao_oauth import build_kakao_auth_url
from app.services.kakao_message_sender import send_kakao_message

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root():
    return {"message": "FastAPI 챗봇 서버 실행 중!"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    return handle_webhook(data)


@app.get("/auth_url")
async def auth_url(user_id: str = Query(..., description="사용자 고유 ID")):
    url = build_kakao_auth_url(user_id)
    return {"auth_url": url}


@app.get("/oauth", response_class=HTMLResponse)
async def oauth(request: Request):
    params = dict(request.query_params)
    result = handle_oauth(params)

    user_id = params.get("state")

    if not user_id:
        return templates.TemplateResponse(
            "failure.html",
            {"request": request, "error": "state(user_id)가 전달되지 않았습니다."}
        )

    if "error" in result:
        # 인증 실패
        auth_url = build_kakao_auth_url(user_id)
        send_kakao_message(
            user_id,
            f"❌ 인증에 실패했습니다. 다시 인증해 주세요: {auth_url}"
        )
        return templates.TemplateResponse(
            "failure.html",
            {"request": request}
        )

    else:
        # 인증 성공
        send_kakao_message(
            user_id,
            "✅ 인증이 완료되었습니다. 무엇을 도와드릴까요?"
        )
        return templates.TemplateResponse(
            "success.html",
            {"request": request}
        )