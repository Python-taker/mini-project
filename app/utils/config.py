import json
from pathlib import Path

def load_settings() -> dict:
    settings_path = Path(__file__).resolve().parent.parent / "config" / "settings.json"
    with open(settings_path, encoding="utf-8") as f:
        return json.load(f)

settings = load_settings()

BASE_URL = settings.get("BASE_URL")
