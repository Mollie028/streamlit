import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

# ✅ 後端 API URL
API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 頁面設定
st.set_page_config(page_title="名片辨識系統", layout="centered")

# ✅ 若已登入則跳轉首頁
if st.session_state.get("access_token"):
    switch_page("首頁")

# ✅ 顯示登入介面
st.title("🔐 請先登入")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    with st.spinner("登入中..."):
        try:
            res = requests.post(
                f"{API_BASE}/login",
                json={"username": username, "password": password}
            )
            if res.status_code == 200:
                access_token = res.json()["access_token"]
                st.session_state["access_token"] = res.json()["access_token"]
                st.success("✅ 登入成功，前往首頁")
                switch_page("首頁")
            else:
                st.error("❌ 登入失敗，請檢查帳號密碼")
        except Exception as e:
            st.error(f"伺服器錯誤：{e}")
