"""
manufacturer_brand_crawler.py
────────────────────────────────────────────────────────────
- 다나와 상품 상세 페이지에서 제조사/브랜드를 크롤링
- 저장된 값은 추후 로직에 활용됨
- 크롤링 로직은 crawl_spec_options() 함수로 분리

📌 주의 사항
1. chromedriver는 OS별로 사전에 설치되어야 함 (자동 설치 지원)
2. WINDOWS_USER 상수는 로컬 윈도우 환경에 맞게 수정
3. 출력 경로는 OS별로 다름
"""

import platform
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =====================================================
# 0️⃣ 전역 설정
# =====================================================
WINDOWS_USER = "sdg15"  # ⚠️ 로컬 윈도우 계정명에 맞게 수정


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
# 2️⃣ Selenium Driver 세팅
# =====================================================
def setup_selenium_driver() -> webdriver.Chrome:
    """
    OS별 크롬드라이버 준비 및 headless 설정
    """
    chromedriver_installer = import_chromedriver_installer()
    if chromedriver_installer and not chromedriver_installer.setup_chromedriver():
        print("❌ chromedriver 설치 실패")
        sys.exit(1)

    os_name = platform.system()
    if os_name == "Windows":
        driver_path = Path("C:/chromedriver/chromedriver.exe")
    elif os_name == "Linux":
        driver_path = Path.home() / "kakaotalk_chatbot/mini-project/crawling/chromedriver-linux64/chromedriver"
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

    driver = webdriver.Chrome(service=Service(str(driver_path)), options=options)
    driver.implicitly_wait(1)

    return driver


# =====================================================
# 3️⃣ 크롤링 로직
# =====================================================
def crawl_spec_options(url: str) -> dict:
    """
    옵션 네비게이션 영역 크롤링
    - 옵션이 존재하면 옵션만 반환
    - 옵션이 없으면 nav_3depth를 대신 크롤링
    """
    driver = setup_selenium_driver()
    wait = WebDriverWait(driver, 3)  # 명시적 대기 3초

    driver.get(url)

    result = {}

    try:
        div_spec_list = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "option_nav")))
        dl_spec_items = div_spec_list.find_elements(By.CLASS_NAME, "spec_item")
        count = 0
        for dl in dl_spec_items:
            try:
                input_elem = dl.find_element(By.CSS_SELECTOR, "input[data-attribute-name]")
                attr_name = input_elem.get_attribute("data-attribute-name").strip()
                if attr_name not in result:
                    result[attr_name] = []
                labels = dl.find_elements(By.CSS_SELECTOR, "li.sub_item > label")
                result[attr_name].extend(
                    label.get_attribute("title").strip()
                    for label in labels
                    if label.get_attribute("title")
                )
            except Exception as e:
                print(f"⚠️ spec_item 처리 중 오류: {e}")
                continue
            count += 1
            if count == 2:
                break

    except Exception as e:
        print(f"⚠️ 옵션 네비게이션 크롤링 실패: {e}")
    
    # 중복 제거 후 정렬
    result = {k: sorted(set(v)) for k, v in result.items()}

    # 옵션값이 하나도 없을 경우에만 nav 크롤링
    if not result:
        print("ℹ️ 옵션값이 없어 nav_3depth를 대신 크롤링합니다.")
        nav_dict = {}
        try:
            ul_nav_3depth = driver.find_element(By.CLASS_NAME, "nav_3depth")
            for a in ul_nav_3depth.find_elements(By.CSS_SELECTOR, "a.nav_link"):
                txt_elem = a.find_element(By.CSS_SELECTOR, "span.link_txt")
                txt = txt_elem.text.strip()
                href = a.get_attribute("href").strip()
                if txt and href:
                    nav_dict[txt] = href
        except Exception as e:
            print(f"⚠️ nav_3depth 크롤링 실패: {e}")
        
        if nav_dict:
            result["nav"] = nav_dict

    driver.quit()
    return result


# =====================================================
# 4️⃣ 메인 실행 로직
# =====================================================
def main():
    """
    CLI 테스트용
    """
    url = "https://prod.danawa.com/list/?cate=11254120&15main_22_02"
    result = crawl_spec_options(url)

    print("\n📄 최종 결과:")
    print(result)

    return result


if __name__ == "__main__":
    main()
