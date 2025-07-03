import requests
import sys
import os

# 加入根目錄到模組路徑
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.config import API_BASE

def create_user(username, password, role="user", company_name=None):
    try:
        res = requests.post(
            f"{API_BASE}/register",
            json={
                "username": username,
                "password": password,
                "role": role,
                "company_name": company_name
            }
        )
        if res.status_code == 200:
            return True
        else:
            print("❌ 註冊失敗：", res.text)
            return False
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
            data = res.json()
            return "admin" if data.get("is_admin") else "user"
        else:
            print("❌ 登入失敗：", res.text)
            return None
    except Exception as e:
        print("❌ 登入 API 呼叫失敗：", e)
        return None
