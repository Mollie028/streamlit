import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import psycopg2
from core.config import API_BASE, DB_URL


def create_user(username, password, role="user", company_name=None):
    try:
        body = {
            "username": username,
            "password": password,
            "role": role,
            "company_name": company_name
        }
        print("📤 發送註冊請求：", body)
        res = requests.post(f"{API_BASE}/register", json=body)
        print("📥 後端回應狀態碼：", res.status_code)
        print("📥 後端回應內容：", res.text)

        return res.status_code == 200
    except Exception as e:
        print("❌ 註冊 API 呼叫失敗：", e)
        return False

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
