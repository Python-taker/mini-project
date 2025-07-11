"""
affirmative_llm.py
──────────────────────────────
- 사용자 입력(utterance)을 기반으로
  LLM에게 긍정 여부를 판별하도록 요청하고 결과를 반환
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

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
async def _call_affirmative_llm(utterance: str) -> bool:
    """
    OpenAI를 호출해 사용자 입력이 긍정인지 아닌지를 판별합니다.
    """
    # 🔷 프롬프트 로드
    system_prompt = load_text_file(PROMPT_DIR / "is_affirmative_system_prompt.txt")
    user_prompt_template = load_text_file(PROMPT_DIR / "is_affirmative_user_prompt.txt")
    user_prompt = user_prompt_template.format(utterance=utterance.strip())

    # 🔷 LLM 호출
    try:
        response = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
    except Exception as e:
        print(f"❌ OpenAI API 호출 실패: {e}")
        return False

    content = response.choices[0].message.content.strip()

    # 🔷 후처리
    if content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json") or content.lower().startswith("python"):
            content = content.split("\n", 1)[-1].strip()

    # 긍정 판단
    return content.upper().startswith("YES")


# =====================================================
# is_affirmative 함수 (외부 호출 진입점)
# =====================================================
async def is_affirmative(utterance: str) -> bool:
    """
    외부에서 호출하는 함수: 동기 → 비동기 실행
    """
    return await _call_affirmative_llm(utterance)


# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    import asyncio

    example_utterance = "네 진행할게요."

    print(f"입력: {example_utterance}")
    result = asyncio.run(is_affirmative(example_utterance))
    print("\n출력:", result)
