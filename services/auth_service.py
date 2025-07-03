# services/auth_service.py

import requests

API_BASE = "https://ocr-whisper-production-2.up.railway.app"

def check_login(username, password):
    url = f"{API_BASE}/login"
    data = {"username": username, "password": password}
    try:
        res = requests.post(url, json=data)
        if res.status_code == 200:
            res_data = res.json()
            return "admin" if res_data.get("is_admin") else "user"
        else:
            print("❌ 登入失敗：", res.status_code, res.text)
            return None
    except Exception as e:
        print("❌ 登入例外：", e)
        return None


def create_user(username, password, role):
    url = f"{API_BASE}/register"
    data = {
        "username": username,
        "password": password,
        "is_admin": role == "admin"
    }
    try:
        res = requests.post(url, json=data)
        if res.status_code == 200:
            print("✅ 註冊成功")
            return True
        else:
            print("❌ 註冊失敗：", res.status_code, res.text)
            return False
    except Exception as e:
        print("❌ 註冊例外：", e)
        return False
