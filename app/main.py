"""
main.py
──────────────────────────────
- FastAPI 카카오톡 챗봇 서버 진입점
- webhook / oauth 라우터 처리
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.webhook_handler import handle_webhook
from app.services.oauth_handler import handle_oauth
from app.utils.kakao_oauth import build_kakao_auth_url
from app.services.kakao_message_sender import send_kakao_message

app = FastAPI(
    title="KakaoTalk Shopping Assistant Bot",
    description="FastAPI 기반 카카오 챗봇 서버",
    version="1.0.0",
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", summary="헬스 체크")
async def root() -> dict:
    """
    서버 상태 확인용 엔드포인트
    """
    return {"message": "FastAPI 챗봇 서버 실행 중!"}


@app.post("/webhook", summary="카카오톡 Webhook")
async def webhook(request: Request) -> dict:
    """
    카카오톡에서 들어오는 Webhook 이벤트 처리

    Args:
        request (Request): 요청 객체

    Returns:
        dict: 카카오톡에 응답할 JSON
    """
    data = await request.json()
    return await handle_webhook(data)


@app.get("/auth_url", summary="카카오 인증 URL 생성")
async def auth_url(
    user_id: str = Query(..., description="사용자 고유 ID (state로 전달됨)")
) -> dict:
    """
    카카오 인증용 URL 생성

    Args:
        user_id (str): 사용자 ID

    Returns:
        dict: 인증 URL
    """
    url = build_kakao_auth_url(user_id)
    return {"auth_url": url}


@app.get("/oauth", response_class=HTMLResponse, summary="카카오 OAuth 콜백")
async def oauth(request: Request) -> HTMLResponse:
    """
    카카오 인증 성공/실패 콜백 처리

    Args:
        request (Request): 요청 객체

    Returns:
        HTMLResponse: 인증 결과 페이지
    """
    params = dict(request.query_params)
    result = handle_oauth(params)

    user_id = params.get("state")

    if not user_id:
        return templates.TemplateResponse(
            "failure.html",
            {"request": request, "error": "state(user_id)가 전달되지 않았습니다."},
        )

    if "error" in result:
        # 인증 실패
        auth_url = build_kakao_auth_url(user_id)
        send_kakao_message(
            user_id,
            f"❌ 인증에 실패했습니다. 다시 인증해 주세요: {auth_url}"
        )
        return templates.TemplateResponse("failure.html", {"request": request})

    # 인증 성공
    send_kakao_message(
        user_id,
        "✅ 인증이 완료되었습니다. 무엇을 도와드릴까요?"
    )
    return templates.TemplateResponse("success.html", {"request": request})
