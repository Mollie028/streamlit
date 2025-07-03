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
            # 回傳錯誤訊息內容
            return res.text
    except Exception as e:
        return f"❌ API 呼叫失敗：{e}"

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
