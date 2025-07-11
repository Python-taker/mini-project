"""
category_structure_builder.py
────────────────────────────────────────────────────────
- 다나와 메인 카테고리 구조를 크롤링하여 JSON으로 저장
- 저장된 JSON은 OpenAI ChatCompletion 시스템 프롬프트에 사용됨
- 파일 존재 여부는 외부에서 판단하며, 없을 경우 이 모듈을 호출해 데이터 생성

!! 주의 사항 !!
1. chromedriver는 OS별로 사전에 설치되어야 함 (자동 설치 지원)
2. WINDOWS_USER 상수는 로컬 윈도우 환경에 맞게 수정
3. 크롤링 결과는 OS별로 다른 경로에 저장됨

📌 호출 관계
- 단독 실행 가능 (CLI 테스트용)
"""

import platform
import sys
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import requests

# =====================================================
# 0️⃣ 전역 설정
# =====================================================
WINDOWS_USER = "sdg15"  # 로컬 윈도우 계정명 (환경에 맞게 수정)

# =====================================================
# 1️⃣ chromedriver_installer 임포트 (OS별)
# =====================================================
def import_chromedriver_installer():
    """
    OS별 chromedriver_installer.py를 경로에 추가 후 임포트
    """
    os_name = platform.system()
    if os_name == "Windows":
        installer_path = Path(f"C:/Users/{WINDOWS_USER}")
    elif os_name == "Linux":
        installer_path = Path.home() / "kakaotalk_chatbot/mini-project/selenium_utils"
    else:
        raise RuntimeError(f"Unsupported OS: {os_name}")

    if not (installer_path / "chromedriver_installer.py").exists():
        raise FileNotFoundError(f"{installer_path}/chromedriver_installer.py 가 존재하지 않습니다.")

    sys.path.append(str(installer_path))
    import chromedriver_installer
    return chromedriver_installer

# =====================================================
# 2️⃣ 메인 페이지에서 카테고리 href 수집
# =====================================================
def extract_category_hrefs(url: str) -> list[str]:
    """
    다나와 메인 페이지에서 메인 카테고리 href 목록 추출
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    div_category = soup.find('div', attrs={"id": "category"})
    if not div_category:
        raise ValueError("div with id='category' not found")

    a_list = div_category.find_all("a", class_="category__list__btn")
    return [a.get('href') for a in a_list if a.get('href')]

# =====================================================
# 3️⃣ Selenium으로 카테고리 트리 크롤링
# =====================================================
def crawl_category_structure(driver: webdriver.Chrome, hrefs: list[str]) -> dict:
    """
    Selenium을 사용해 카테고리 트리 크롤링 → dict 반환
    """
    result = {}
    actions = ActionChains(driver)

    for idx, href in enumerate(hrefs, 1):
        print(f"📊 {idx}/{len(hrefs)} - {href}")
        top_btn = driver.find_element(By.CSS_SELECTOR, f'a[href="{href}"]')
        actions.move_to_element(top_btn).click().perform()
        driver.implicitly_wait(3)

        layer = driver.find_element(By.ID, href.lstrip("#"))
        li_rows = layer.find_elements(By.CSS_SELECTOR, "li.category__depth__row.depth1")

        top_name = top_btn.text.strip()
        if not top_name:
            continue

        result.setdefault(top_name, {})
        current_key = None

        for row in li_rows:
            actions.move_to_element(row).perform()
            driver.implicitly_wait(1)

            if "dp_dot" in row.get_attribute("class"):
                for txt_elem in row.find_elements(By.CLASS_NAME, "category__depth__txt"):
                    clean_txt = txt_elem.text.strip()
                    if "\n" in clean_txt:
                        clean_txt = clean_txt.split("\n", 1)[1].strip()
                    href_attr = txt_elem.find_element(By.XPATH, "..").get_attribute("href")

                    if not clean_txt or not href_attr:
                        continue

                    if href_attr.strip() == "https://www.danawa.com/#":
                        current_key = clean_txt
                        result[top_name][current_key] = []
                        print(f"  📂 {current_key}")
                        continue

                    if current_key:
                        result[top_name][current_key].append((clean_txt, href_attr))
                        print(f"    ➡️ {clean_txt} - {href_attr}")

    print("✅ 카테고리 크롤링 완료")
    return result

# =====================================================
# 4️⃣ JSON으로 저장 (원본 + 시스템프롬프트용 + 중간키+하위목록)
# =====================================================
def save_all_json(result: dict, base_dir: Path):
    """
    크롤링 결과를 JSON으로 저장
    - category_structure.json (원본)
    - category_structure_prompt.json (메인/중간 키만: 시스템프롬프트용)
    - category_structure_keys.json (중간키 + 하위 이름들)
    """
    original_path = base_dir / "category_structure.json"
    prompt_path = base_dir / "category_structure_prompt.json"
    keys_full_path = base_dir / "category_structure_keys.json"

    # 1️⃣ 원본 저장
    with open(original_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"💾 원본 JSON 저장: {original_path}")

    # 2️⃣ 메인/중간키만 저장 → 시스템프롬프트용
    keys_only = {}
    for top, mid_dict in result.items():
        keys_only[top] = list(mid_dict.keys())

    with open(prompt_path, "w", encoding="utf-8") as f:
        json.dump(keys_only, f, ensure_ascii=False, indent=2)
    print(f"💾 시스템프롬프트용 JSON 저장: {prompt_path}")

    # 3️⃣ 중간키 + 하위 이름들 저장
    simplified = {}
    for top, mid_dict in result.items():
        simplified[top] = {}
        for mid, lst in mid_dict.items():
            simplified[top][mid] = [name for name, _ in lst]

    with open(keys_full_path, "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)
    print(f"💾 중간키+하위목록 JSON 저장: {keys_full_path}")

# =====================================================
# 5️⃣ 메인 실행 로직
# =====================================================
def main():
    """
    CLI 테스트용 진입점
    """
    os_name = platform.system()
    chromedriver_installer = import_chromedriver_installer()
    if chromedriver_installer and not chromedriver_installer.setup_chromedriver():
        print("❌ chromedriver 설치 실패")
        sys.exit(1)

    if os_name == "Windows":
        driver_path = Path("C:/chromedriver/chromedriver.exe")
        output_dir = Path(f"C:/Users/{WINDOWS_USER}")
    elif os_name == "Linux":
        driver_path = Path.home() / "kakaotalk_chatbot/mini-project/crawling/chromedriver-linux64/chromedriver"
        output_dir = Path.home() / "kakaotalk_chatbot/mini-project/storage"
    else:
        print(f"❌ Unsupported OS: {os_name}")
        sys.exit(1)

    if not driver_path.exists():
        print(f"❌ chromedriver not found: {driver_path}")
        sys.exit(1)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    url = "https://www.danawa.com/"
    hrefs = extract_category_hrefs(url)

    driver = webdriver.Chrome(service=Service(str(driver_path)), options=options)
    driver.get(url)
    driver.implicitly_wait(3)

    result = crawl_category_structure(driver, hrefs)
    driver.quit()

    output_dir.mkdir(parents=True, exist_ok=True)
    save_all_json(result, output_dir)

if __name__ == "__main__":
    main()
