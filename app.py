import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

st.set_page_config(page_title="登入", page_icon="🔐")

if st.session_state.get("access_token"):
    switch_page("首頁")  # ✅ 中文檔名 OK，確保你真的有 pages/首頁.py
    st.stop()

st.title("🔐 登入頁面")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    res = requests.post(f"{API_BASE}/login", json={"username": username, "password": password})
    if res.status_code == 200:
        token = res.json().get("access_token")
        st.session_state["access_token"] = token
        st.success("✅ 登入成功，正在跳轉...")
        switch_page("首頁")  # ✅ 這裡要跟 pages 資料夾裡的 py 檔案完全一致
    else:
        st.error("❌ 登入失敗，請確認帳密")
