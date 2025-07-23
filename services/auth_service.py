import os
import streamlit as st
import requests
import psycopg2
from core.config import API_BASE

DB_URL = os.getenv("DB_URL")

# ✅ 建立新帳號
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

# ✅ 登入驗證 + 寫入 token 與 user_info
def check_login(username, password):
    try:
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200:
            data = res.json()

            # ✅ 儲存 access_token 給 API 使用
            st.session_state["access_token"] = data["access_token"]

            # ✅ 儲存登入者資訊給 is_logged_in() 判斷用
            st.session_state["user_info"] = {
                "username": username,
                "role": data.get("role", "user"),
                "company_name": data.get("company_name", "")
            }

            return st.session_state["user_info"]
        else:
            print("❌ 登入失敗：", res.text)
            return None
    except Exception as e:
        print("❌ 登入 API 錯誤：", e)
        return None

# ✅ 測試資料庫連線
def test_db_connection():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.close()
        print("✅ 成功連線資料庫")
        return True
    except Exception as e:
        print("❌ 無法連線資料庫：", e)
        return False

# ✅ 登入狀態檢查
def is_logged_in():
    """回傳使用者登入資訊（dict），若未登入則回傳 None"""
    user_info = st.session_state.get("user_info")
    if isinstance(user_info, dict) and "username" in user_info:
        return user_info
    return None

# ✅ 登出按鈕
def logout_button():
    if st.button("🔓 登出", key="logout_button"):
        st.session_state.clear()
        st.rerun()
