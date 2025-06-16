import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

# ✅ 基本設定
st.set_page_config(page_title="登入", page_icon="🔐")

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 如果已登入就跳首頁
if st.session_state.get("access_token"):
    switch_page("首頁")

# ✅ 登入畫面
st.title("🔐 名片辨識系統登入")
username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            access_token = res.json().get("access_token")
            if access_token:
                st.session_state["access_token"] = access_token
                st.success("✅ 登入成功，導向首頁...")
                switch_page("首頁")
            else:
                st.error("❌ 後端未傳回 access_token")
        else:
            st.error("❌ 登入失敗，請確認帳密是否正確")
    except Exception as e:
        st.error(f"🚨 登入錯誤：{e}")
