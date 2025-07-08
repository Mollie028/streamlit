import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import psycopg2
from core.config import API_BASE


def create_user(username, password, role="user", company_name=None):
    try:
        body = {
            "username": username,
            "password": password,
            "company_name": company_name or "",  
            "role": role
        }

        print("📤 發送註冊請求：", body)
        res = requests.post(f"{API_BASE}/register", json=body)
        print("📥 後端回應狀態碼：", res.status_code)
        print("📥 後端回應內容：", res.text)

        if res.status_code == 200:
            return True
        else:
            # 嘗試回傳後端錯誤內容
            try:
                return res.json().get("detail", f"錯誤狀態碼：{res.status_code}")
            except Exception:
                return f"註冊失敗，錯誤碼 {res.status_code}，內容：{res.text}"
    except Exception as e:
        print("❌ 註冊 API 呼叫失敗：", e)
        return f"⚠️ 呼叫失敗：{e}"


def check_login(username, password):
    try:
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200:
            return res.json().get("role", "user")
        else:
            print("❌ 登入失敗：", res.text)
            return None
    except Exception as e:
        print("❌ 登入 API 錯誤：", e)
        return None

def test_db_connection():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.close()
        print("✅ 成功連線資料庫")
        return True
    except Exception as e:
        print("❌ 無法連線資料庫：", e)
        return False
