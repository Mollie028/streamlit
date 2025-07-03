import requests

API_BASE = "https://ocr-whisper-production-2.up.railway.app"


def check_login(username, password):
    try:
        payload = {"username": username, "password": password}
        res = requests.post(f"{API_BASE}/login", json=payload)

        if res.status_code == 200:
            data = res.json()
            # 回傳角色：'admin' 或 'user'
            return data["is_admin"] and "admin" or "user"
        else:
            print("❌ 登入失敗：", res.status_code, res.text)
    except Exception as e:
        print("❌ 登入 API 發生錯誤：", e)
    return None


def create_user(username, password, role="user"):
    try:
        payload = {
            "username": username,
            "password": password,
            "role": role
        }
        res = requests.post(f"{API_BASE}/register", json=payload)

        if res.status_code == 200:
            print("✅ 註冊成功")
            return True
        else:
            print("❌ 註冊失敗：", res.status_code, res.text)
    except Exception as e:
        print("❌ 註冊 API 發生錯誤：", e)

    return False
