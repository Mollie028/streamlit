import sys
import os
import streamlit as st  # ✅ 新增：用於登入狀態與登出按鈕
import requests
import psycopg2
from core.config import API_BASE

# 如果有需要加上資料庫連線字串，可從環境變數或 config 中載入
# 這裡假設你自己有設定 DB_URL（若沒設定會報錯）
DB_URL = os.getenv("DB_URL")  # ✅ 可自訂為你的資料庫連線字串

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

# ✅ 登入驗證
def check_login(username, password):
    try:
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200:
            data = res.json()
            return {
                "role": data.get("role", "user"),
                "company_name": data.get("company_name", "")
            }
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
    return 'access_token' in st.session_state and st.session_state['access_token'] != ""

# ✅ 登出按鈕
def logout_button():
    if st.button("🔓 登出"):
        st.session_state.clear()
        st.rerun()
