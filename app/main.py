from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI 챗봇 서버 실행 중!"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(f"📩 받은 데이터: {data}")

    # 여기서 data를 LLM에 넘기고 처리 결과를 만들어야 함
    # 지금은 테스트용으로 메시지를 그대로 돌려보냄
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"받은 메시지: {data}"
                    }
                }
            ]
        }
    }
