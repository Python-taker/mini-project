"""
category_match_llm.py
──────────────────────────────
- 사용자 입력(utterance)과 bot_raw_result(dict)를 기반으로
  LLM에게 중간 키워드 + 세부 항목 매칭을 요청하고 결과를 반환
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
import ast

# =====================================================
# 환경 설정 & OpenAI 클라이언트
# =====================================================
load_dotenv()
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = PROJECT_ROOT / "prompts"

# =====================================================
# 유틸 함수
# =====================================================
def load_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# =====================================================
# LLM 호출
# =====================================================
async def _call_category_match_llm(utterance: str, bot_raw_result: dict) -> list:
    """
    OpenAI를 호출해 사용자 입력과 bot_raw_result를 비교하여
    중간 키워드 + 세부 항목 쌍을 반환하거나 실패 메시지를 반환
    """
    # 🔷 bot_raw_result를 문자열로 변환
    bot_raw_str = json.dumps(bot_raw_result, ensure_ascii=False, indent=2)

    # 🔷 프롬프트 로드
    system_prompt = load_text_file(PROMPT_DIR / "category_match_system_prompt.txt")
    user_prompt_template = load_text_file(PROMPT_DIR / "category_match_user_prompt.txt")
    user_prompt = user_prompt_template.format(
        utterance=utterance.strip(),
        bot_raw_result=bot_raw_str
    )

    # 🔷 LLM 호출
    try:
        response = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
    except Exception as e:
        print(f"❌ OpenAI API 호출 실패: {e}")
        return [False, "죄송합니다. 현재 서비스에 문제가 있습니다. 다시 시도해 주세요."]

    content = response.choices[0].message.content.strip()

    # 🔷 후처리: ```json … ``` 제거
    if content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json") or content.lower().startswith("python"):
            content = content.split("\n", 1)[-1].strip()

    # 🔷 안전하게 파싱
    parsed = None
    for parser in (json.loads, ast.literal_eval):
        try:
            candidate = parser(content)
            if isinstance(candidate, list):
                parsed = candidate
                break
        except Exception:
            continue

    if parsed and isinstance(parsed, list) and isinstance(parsed[0], bool):
        return parsed
    else:
        print("⚠️ LLM 응답 파싱 실패")
        print("원본 응답:", content)
        return [False, "죄송합니다. 입력하신 내용을 이해하지 못했습니다. 다시 한번 시도해 주세요."]


# =====================================================
# category_match 함수 (외부 호출 진입점)
# =====================================================
async def category_match(utterance: str, bot_raw_result: dict) -> list:
    """
    외부에서 호출하는 함수: 동기 → 비동기 실행
    """
    return await _call_category_match_llm(utterance, bot_raw_result)


# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    import asyncio

    example_utterance = "세에차"
    example_bot_raw_result = {
        "자동차용품": ["오일/첨가제/필터", "세차/와이퍼/방향제", "부품/외장/안전"],
        "부품/외장/안전": ["브레이크패드", "점화플러그/부품"]
    }

    print(f"입력: {example_utterance}")
    output = asyncio.run(category_match(example_utterance, example_bot_raw_result))
    print("\n출력:")
    print(json.dumps(output, ensure_ascii=False, indent=2))
