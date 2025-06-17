import streamlit as st
import requests

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

def render():
    # ✅ 一定要第一行
    st.set_page_config(page_title="登入", page_icon="🔐")
    st.title("🔐 名片辨識系統登入")

    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200 and res.json().get("access_token"):
            st.session_state.access_token = res.json()["access_token"]
            st.session_state.page = "首頁"
            st.experimental_rerun()
        else:
            st.error("❌ 登入失敗，請確認帳號密碼")
