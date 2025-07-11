"""
chromedriver_installer.py
────────────────────────────────────────────────────────
- OS에 맞는 ChromeDriver를 지정된 경로에 자동 설치
- 리눅스: ~/kakaotalk_chatbot/mini-project/crawling/chromedriver-linux64/chromedriver
- 윈도우: C:\chromedriver\chromedriver.exe

!! 주의 사항 !!
1. 설치 경로는 OS별로 하드코딩되어 있으므로 다른 경로로 설치 시 코드 수정 필요
2. Google Chrome 설치가 선행되어야 함

📌 호출 관계
- 단독 실행 가능 (CLI 테스트)
- 다른 모듈에서 `setup_chromedriver()`를 호출해도 됨
"""

import platform
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

# =====================================================
# 0️⃣ 상수 정의
# =====================================================
CHROME_VERSION = "138.0.7204.94"
BASE_URL = f"https://storage.googleapis.com/chrome-for-testing-public/{CHROME_VERSION}/"

SYSTEM_MAP = {
    "Linux": "linux64",
    "Windows": "win64",
    "Darwin": "mac-x64",
}

# =====================================================
# 1️⃣ webdriver-manager 설치 여부 + 드라이버 존재 여부 체크
# =====================================================
def check_webdriver_manager_and_driver() -> bool:
    """
    webdriver-manager 설치 여부 및 OS별 chromedriver 경로 존재 확인
    """
    try:
        import webdriver_manager  # noqa: F401
    except ImportError:
        return False

    system_name = platform.system()
    if system_name == "Linux":
        chromedriver_path = Path(__file__).resolve().parents[2] / "mini-project" / "crawling" / "chromedriver-linux64" / "chromedriver"
    elif system_name == "Windows":
        chromedriver_path = Path(r"C:\chromedriver\chromedriver.exe")
    else:
        return False  # 지원하지 않는 OS

    return chromedriver_path.exists()

# =====================================================
# 2️⃣ 크롬드라이버 다운로드 + 압축 해제
# =====================================================
def download_and_extract_chromedriver(dest_dir: Path, target: str):
    """
    크롬드라이버를 지정 폴더에 다운로드 후 압축 해제
    """
    zip_name = f"chromedriver-{target}.zip"
    url = BASE_URL + f"{target}/{zip_name}"
    zip_path = dest_dir / zip_name

    print(f"📥 Downloading chromedriver from:\n{url}")
    urlretrieve(url, zip_path)

    print(f"📦 Extracting to: {dest_dir}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)

    # === 실행 권한 부여 (Linux & macOS)
    system_name = platform.system()
    if system_name in ("Linux", "Darwin"):
        chromedriver_path = dest_dir / "chromedriver-linux64" / "chromedriver"
        if chromedriver_path.exists():
            chromedriver_path.chmod(0o755)
            print(f"🔑 실행 권한 부여: {chromedriver_path}")

    zip_path.unlink()
    print("✅ chromedriver 설치 완료.")

# =====================================================
# 3️⃣ 메인 로직: 크롬드라이버 설치 보장
# =====================================================
def setup_chromedriver() -> bool:
    """
    크롬드라이버 설치를 보장하는 메인 로직
    다른 파일에서 호출 시 True/False 반환
    """
    try:
        if check_webdriver_manager_and_driver():
            print("✅ webdriver-manager 와 chromedriver 가 이미 설치되어 있습니다. 별도 조치 필요 없음.")
            return True

        system_name = platform.system()
        if system_name not in SYSTEM_MAP:
            print(f"❌ Unsupported OS: {system_name}")
            return False

        target = SYSTEM_MAP[system_name]

        if system_name == "Linux":
            script_path = Path(__file__).resolve()
            base_dir = script_path.parents[2] / "mini-project" / "crawling"
            chromedriver_path = base_dir / "chromedriver-linux64" / "chromedriver"

            if chromedriver_path.exists():
                print(f"✅ chromedriver 가 이미 존재합니다: {chromedriver_path}")
                return True

            base_dir.mkdir(parents=True, exist_ok=True)
            download_and_extract_chromedriver(base_dir, target)
            print(f"chromedriver 위치: {chromedriver_path}")
            return True

        elif system_name == "Windows":
            base_dir = Path(r"C:\chromedriver")
            base_dir.mkdir(parents=True, exist_ok=True)

            chromedriver_path = base_dir / "chromedriver.exe"
            if chromedriver_path.exists():
                print(f"✅ chromedriver.exe 가 이미 존재합니다: {chromedriver_path}")
                return True

            download_and_extract_chromedriver(base_dir, target)
            extracted_dir = base_dir / "chromedriver-win64"
            extracted_driver = extracted_dir / "chromedriver.exe"

            extracted_driver.replace(chromedriver_path)

            if extracted_dir.exists():
                for item in extracted_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                extracted_dir.rmdir()

            print(f"chromedriver 위치: {chromedriver_path}")
            return True

        else:
            print(f"❌ Unsupported OS: {system_name}")
            return False

    except Exception as e:
        print(f"❌ 크롬드라이버 설치 중 오류 발생: {e}")
        return False

# =====================================================
# 4️⃣ CLI 테스트
# =====================================================
if __name__ == "__main__":
    print(setup_chromedriver())
