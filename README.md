## Mini-project
SSAFY 2025.07.09 ~ 2025.07.11

## Mini-Project Setup Guide

---

## 📦 Requirements
- Python 3.10.x
- Tesseract OCR
- OpenAI API Key
- Kakao Developers REST API Key
- Upstage Solar Pro API Key (Optional)

---

## 🔷 Windows
✅ Python 3.10 다운로드:  
👉 [https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)

✅ Tesseract OCR 다운로드:  
👉 [https://github.com/UB-Mannheim/tesseract/releases](https://github.com/UB-Mannheim/tesseract/releases)

설치 후 Tesseract 경로를 환경 변수 `PATH`에 추가해야 합니다. (보통 자동 설정됩니다.)

---

## 🔷 Linux
✅ Python 3.10: 대부분 기본 설치됨. 없을 경우:
```bash
sudo apt install python3.10 python3.10-venv
```

✅ Tesseract OCR 설치:
```bash
sudo apt update
sudo apt install tesseract-ocr
```

---

## 🚀 Setup

## 🔷 Windows
PowerShell이나 CMD에서:
```cmd
setup.bat
```
## 🔷 Linux / macOS
터미널에서:
```bash
bash setup.sh
```
설치가 끝나면 가상환경 안에서 실행하세요:
```bash
source .venv/bin/activate
```

---

## 📌 Notes
- `.venv/` 안에 가상환경이 생성됩니다.
- `requirements.txt`로 필요한 패키지가 자동 설치됩니다.
- `tokens.json`과 `.env`파일은 절대 git에 커밋하지 마세요.
- 프로젝트를 실행하기 전에 반드시 `.env`파일과 `config/settings.json`을 작성해야 합니다.

---

## 🌱 환경 변수 설정
루트 디렉토리에 `.env`파일을 만들어 아래와 같이 작성해 주세요:
```bash
KAKAO_REST_API_KEY=your-kakao-rest-api-key
OPENAI_API_KEY=your-openai-api-key
UPSTAGE_SOLAR_PRO_API_KEY=your-upstage-api-key
```
`.env`파일은 민감한 정보가 포함되므로 절대 깃에 올리지 마세요.

---

## 🛠 설정 파일
config/settings.json에 BASE_URL만 작성하세요:
```json
{
  "BASE_URL": "https://your-ngrok-url.ngrok-free.app"
}
```
`storage/tokens.json`파일은 서버가 자동 생성하며, 유저별 `access_token`정보를 저장합니다.
`git`에 업로드하지 않도록 주의하세요.

---

## 📂 프로젝트 파일 트리
```bash
mini-project/
├── app/
│   ├── main.py                # FastAPI 엔트리포인트
│   ├── config/
│   │   └── settings.json      # BASE_URL 설정
│   │
│   ├── routers/               # (비어있음, 추후 라우터 분리용)
│   │
│   ├── services/
│   │   ├── auth_checker.py            # 인증 상태 확인
│   │   ├── category_recommendation_service.py   # 카테고리 추천 전체 워크플로
│   │   ├── kakao_message_sender.py   # 카카오톡 메시지 발송
│   │   ├── oauth_handler.py          # OAuth 콜백 처리
│   │   └── webhook_handler.py        # 카카오 webhook 요청 처리
│   │
│   ├── templates/
│   │   ├── failure.html              # 인증 실패 안내 페이지
│   │   └── success.html              # 인증 성공 안내 페이지
│   │
│   └── utils/
│       ├── build_category_dict.py           # 카테고리 dict 구성 유틸
│       ├── config.py                        # settings.json 로드
│       ├── kakao_oauth.py                   # 인증 URL 생성 및 토큰 발급
│       ├── parser.py                        # webhook 요청 파싱
│       ├── recommendation_formatter.py      # 추천 결과 보기 좋게 포맷팅
│       └── session_manager.py               # 유저별 세션 상태 관리
│
├── chatbot_llm/
│   ├── refine_llm.py                 # OpenAI 기반 추천 상세화
│   └── validate_llm.py               # OpenAI 기반 카테고리 유효성 검사
│
├── crawling/
│   ├── test.py                       # 크롤링 테스트 코드
│   └── chromedriver-linux64/            # 크롬드라이버 바이너리 
│       ├── chromedriver                 # 크롬드라이버 실행 파일
│       ├── LICENSE.chromedriver        # 라이선스
│       └── THIRD_PARTY_NOTICES.chromedriver # 서드파티 공지
│
├── llm/                              # (비어있음, LLM 관련 코드 예정)
├── ocr/                              # (비어있음, OCR 코드 예정)
├── stt/                              # (비어있음, STT 코드 예정)
├── stable_diffusion/                # (비어있음, 이미지 생성 예정)
│
├── prompts/                          # LLM 프롬프트 모음
│   ├── refine_system_prompt.txt     # refine system 프롬프트
│   ├── refine_user_prompt.txt       # refine user 프롬프트
│   ├── validate_system_prompt.txt   # validate system 프롬프트
│   └── validate_user_prompt.txt     # validate user 프롬프트
│
├── selenium_utils/
│   ├── category_structure_builder.py    # 카테고리 JSON 구조 빌더
│   └── chromedriver_installer.py        # 크롬드라이버 설치 유틸
│
├── storage/
│   ├── category_structure_keys.json     # 카테고리 키 데이터
│   ├── category_structure_prompt.json  # 카테고리 prompt 데이터
│   ├── category_structure.json         # 카테고리 전체 구조
│   ├── token_manager.py                # 사용자 토큰 관리
│   └── tokens.json                     # (자동 생성, 유저 토큰 정보)
│
├── .env                       # API 키 저장 (직접 작성)
├── requirements.txt           # 패키지 의존성 명세
├── README.md                  # 프로젝트 설명
├── setup.bat                  # Windows 설정 스크립트
├── setup.sh                   # Linux/macOS 설정 스크립트
```

---

## 🧹 새로 작업된 기능 (2025.07.11 기준)
✅ 세션 관리 개선
- utils/session_manager.py 추가
- 유저별 stage, 마지막 입력/출력 기록
- history에 raw 추천 결과도 함께 기록

✅ 추천 결과 포맷터
- utils/recommendation_formatter.py 추가
- 추천 결과를 보기 좋은 numbered text 형식으로 출력

✅ webhook 핸들러 리팩토링
- handle_webhook() 내 추천 호출 시 포맷터 적용
- 세션 관리 호출 코드 정리

✅ requirements.txt 갱신
- 최신 FastAPI, OpenAI, python-dotenv 등 반영

---
## ✅ 요약
- .bat → Windows 전용: Python, Tesseract 체크 & 안내
- .sh → Linux/macOS: Python, Tesseract 체크 & 안내
- README.md → 최신 기능까지 문서화
