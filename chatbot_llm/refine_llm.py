"""
refine_llm.py
──────────────────────────────
- validate_llm → build_category_dict 로 생성된 dict를 기반으로
  사용자 입력을 고려해 중간 키 2개 + 각 세부 항목 최대 5개씩 추천
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
async def _call_refine_llm(user_message: str, category_dict: dict) -> list:
    """
    OpenAI를 호출해 사용자 입력을 기반으로
    중간 키 2개 + 각 세부 항목 추천
    """
    # 🔷 category_dict를 문자열로 변환
    category_items_str = ""
    for mid_key, details in category_dict.items():
        category_items_str += f"{mid_key}: {', '.join(details)}\n"

    # 🔷 프롬프트 로드
    system_prompt = load_text_file(PROMPT_DIR / "refine_system_prompt.txt")
    user_prompt_template = load_text_file(PROMPT_DIR / "refine_user_prompt.txt")
    user_prompt = user_prompt_template.format(
        category_data=category_items_str.strip(),
        user_message=user_message.strip()
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
# refine_keywords 함수 (외부 호출 진입점)
# =====================================================
async def refine_keywords(user_message: str, category_dict: dict) -> list:
    """
    외부에서 호출하는 함수: 동기 → 비동기 실행
    """
    return await _call_refine_llm(user_message, category_dict)


# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    # 예시 입력
    import asyncio
    example_input_message = "편하게 쓸 수 있는 사무용 노트북이 필요해"
    example_category_dict = {
        "노트북": [
            "노트북 전체", "AI 노트북", "게이밍 노트북", "APPLE 맥북",
            "인텔 CPU 노트북", "AMD CPU노트북", "다나와 인증 중고",
            "주변기기", "노트북 구매상담"
        ],
        "게이밍 노트북": [
            "게이밍 노트북 전체", "RTX4060~70", "i7 이상 고성능"
        ]
    }

    print(f"입력: {example_input_message}")
    output = asyncio.run(refine_keywords(example_input_message, example_category_dict))
    print("\n출력:")
    print(json.dumps(output, ensure_ascii=False, indent=2))
