import requests
from core.config import API_BASE

def create_user(username, password, role="user", company_name=None):
    try:
        url = f"{API_BASE}/register"
        payload = {
            "username": username,
            "password": password,
            "role": role,
            "company_name": company_name
        }
        print("📤 發送註冊請求：", url)
        print("📦 註冊資料：", payload)

        res = requests.post(url, json=payload)
        print("📥 回應狀態碼：", res.status_code)
        print("📥 回應內容：", res.text)

        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print("❌ 註冊 API 呼叫失敗：", e)
        return False

