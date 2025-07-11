"""
is_valid_choice_llm.py
──────────────────────────────
- 사용자 입력(utterance)과 크롤링된 데이터(crawled_data)를 기반으로
  LLM에게 유효한 선택지를 판별하고 결과를 반환
"""

import os
import ast
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
    """텍스트 파일 로드"""
    return path.read_text(encoding="utf-8").strip()

# =====================================================
# LLM 호출
# =====================================================
async def _call_is_valid_choice_llm(utterance: str, crawled_data: dict) -> dict:
    """
    LLM 호출: 입력과 크롤링 데이터를 기반으로 유효한 선택지를 판별
    :return: {"valid": bool, "matched_choices": List[str] | None, "message": str | None}
    """
    try:
        # 🔷 프롬프트 준비
        crawled_data_str = str(crawled_data)  # dict를 보기 좋게 문자열로
        system_prompt = load_text_file(PROMPT_DIR / "is_valid_choice_system_prompt.txt")
        user_prompt = load_text_file(PROMPT_DIR / "is_valid_choice_user_prompt.txt").format(
            utterance=utterance.strip(),
            crawled_data=crawled_data_str
        )

        # 🔷 LLM API 호출
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
        return {
            "valid": False,
            "matched_choices": None,
            "message": "죄송합니다. 현재 서비스에 문제가 있습니다."
        }

    # 🔷 응답 파싱
    content = response.choices[0].message.content.strip()
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        # 첫 줄이 ``` 또는 ```python 제거
        if lines[0].strip("`").strip().lower() in ("python", ""):
            content = "\n".join(lines[1:-1]).strip()
        else:
            content = content.strip("`").strip()
    elif content.startswith("`") and content.endswith("`"):
        content = content.strip("`").strip()

    try:
        # LLM이 [bool, list|str] 형태로 준다고 가정
        result = ast.literal_eval(content)

        if isinstance(result, list) and len(result) == 2:
            if result[0] is True and isinstance(result[1], list):
                return {
                    "valid": True,
                    "matched_choices": result[1],
                    "message": None
                }
            if result[0] is False and isinstance(result[1], str):
                return {
                    "valid": False,
                    "matched_choices": None,
                    "message": result[1]
                }

    except Exception as e:
        print(f"⚠️ LLM 응답 파싱 실패: {e}")
        print(f"⚠️ 원본 응답: {content}")

    # 최종 실패 처리
    return {
        "valid": False,
        "matched_choices": None,
        "message": "죄송합니다. 입력하신 내용을 이해하지 못했습니다. 다시 시도해 주세요."
    }

# =====================================================
# 외부 진입점 함수
# =====================================================
async def is_valid_choice(utterance: str, crawled_data: dict) -> dict:
    """
    외부에서 호출하는 함수
    """
    return await _call_is_valid_choice_llm(utterance, crawled_data)

# =====================================================
# CLI 테스트
# =====================================================
if __name__ == "__main__":
    import asyncio

    example_utterance = "삼성과 LG 제품이요"
    example_crawled_data = {
        "제조사": ["삼성", "LG", "애플"],
        "브랜드": ["갤럭시", "아이폰"]
    }

    print(f"입력: {example_utterance}")
    output = asyncio.run(is_valid_choice(example_utterance, example_crawled_data))
    print("\n출력:")
    print(output)
