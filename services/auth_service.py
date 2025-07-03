import requests
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
