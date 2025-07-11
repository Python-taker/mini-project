"""
is_valid_choice_llm.py
──────────────────────────────
- 사용자 입력(utterance)과 크롤링된 데이터(crawled_data)를 기반으로
  LLM에게 유효한 선택지를 판별하고 결과 리스트를 반환
"""

import os
import json
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


async def _call_is_valid_choice_llm(utterance: str, crawled_data: dict) -> list:
    """
    LLM 호출: 입력과 크롤링 데이터를 기반으로 유효한 선택 리스트 반환
    """
    try:
        # 🔷 프롬프트 준비
        crawled_data_str = json.dumps(crawled_data, ensure_ascii=False, indent=2)
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
        return [False, "죄송합니다. 현재 서비스에 문제가 있습니다."]

    # 🔷 응답 파싱
    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith(("json", "python")):
            content = content.split("\n", 1)[-1].strip()

    try:
        result = json.loads(content)
        if isinstance(result, list) and len(result) == 2:
            if result[0] is True:
                # 성공
                if isinstance(result[1], list):
                    return [True, result[1]]
            if result[0] is False:
                # 실패
                if isinstance(result[1], str):
                    return [False, result[1]]
    except Exception:
        print("⚠️ LLM 응답 파싱 실패")
        print("원본 응답:", content)

    # 최종 실패 처리
    return [False, "죄송합니다. 입력하신 내용을 이해하지 못했습니다. 다시 한번 시도해 주세요."]


async def is_valid_choice(utterance: str, crawled_data: dict) -> list:
    """
    외부 진입점 함수
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
