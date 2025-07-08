import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import psycopg2
from core.config import API_BASE


def create_user(username, password, company_name=None, is_admin=False):
    payload = {
        "username": username,
        "password": password,
        "company_name": company_name,
        "is_admin": is_admin
    }
    try:
        res = requests.post(f"{API_BASE}/register", json=payload)
        if res.status_code == 200:
            return True
        else:
            return f"錯誤狀態碼：{res.status_code}"
    except Exception as e:
        return f"例外錯誤：{str(e)}"




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
