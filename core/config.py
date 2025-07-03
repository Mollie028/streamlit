import os

API_BASE = os.getenv("API_BASE", "https://ocr-whisper-production-2.up.railway.app")

DB_URL = os.getenv("DATABASE_URL")
print("🧪 Streamlit 前端抓到的 DB_URL 是：", DB_URL)
print("🧪 Streamlit 前端抓到的 API_BASE 是：", API_BASE)
