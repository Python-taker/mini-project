"""
validate_llm.py
──────────────────────────────
- 사용자 입력 → 연관 카테고리 키워드 최대 10개 추출
"""

from openai import AsyncOpenAI
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import ast

# =====================================================
# 환경 설정 & OpenAI 클라이언트
# =====================================================
load_dotenv()
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = PROJECT_ROOT / "prompts"
CATEGORY_KEYS_JSON = PROJECT_ROOT / "storage" / "category_structure_keys.json"

# =====================================================
# 유틸 함수
# =====================================================
def load_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_category_keys() -> dict:
    with open(CATEGORY_KEYS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

# =====================================================
# LLM 호출
# =====================================================
async def _call_validate_llm(user_message: str, category_keys: dict) -> list:
    """
    OpenAI를 호출해 사용자 입력과 카테고리 키를 비교하여 연관 키워드 최대 10개를 추출
    """
    all_keywords = []
    for top, mids in category_keys.items():
        all_keywords.append(top)
        all_keywords.extend(mids.keys())
    keywords_text = "\n".join(all_keywords)

    # 프롬프트 로드
    system_prompt = load_text_file(PROMPT_DIR / "validate_system_prompt.txt")
    user_prompt_template = load_text_file(PROMPT_DIR / "validate_user_prompt.txt")
    user_prompt = user_prompt_template.format(
        keywords=keywords_text,
        user_message=user_message
    )

    # LLM 요청
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
        return [False, "카테고리를 찾지 못했습니다."]

    content = response.choices[0].message.content.strip()

    # 후처리: ```json … ``` 제거
    if content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()
        elif content.lower().startswith("python"):
            content = content[6:].strip()

    # 안전하게 파싱
    parsed = None
    for parser in (json.loads, ast.literal_eval):
        try:
            candidate = parser(content)
            if isinstance(candidate, list) and candidate:
                parsed = candidate
                break
        except Exception:
            continue

    if parsed:
        if isinstance(parsed[0], bool):
            return parsed
        else:
            # 첫 번째 값이 bool이 아니면 강제 실패
            return [False, "카테고리를 찾지 못했습니다."]
    else:
        print("⚠️ LLM 응답 파싱 실패")
        print("원본 응답:", content)
        return [False, "카테고리를 찾지 못했습니다."]


# =====================================================
# validate_keywords 함수 (외부 호출 진입점)
# =====================================================
async def validate_keywords(user_message: str) -> list:
    """
    외부에서 호출하는 함수: 동기 → 비동기 실행
    """
    import asyncio

    category_keys = load_category_keys()
    return await _call_validate_llm(user_message, category_keys)

# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(
        validate_keywords("키보드를 살건데, 그렇게 비싼거는 필요없고 적당한 기계식키보드를 원해")
    )
    print(result)
