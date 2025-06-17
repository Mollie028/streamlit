import streamlit as st
import requests

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

def render():
    st.set_page_config(page_title="請先登入", page_icon="🔐")
    st.title("🔐 請先登入")

    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200 and (token := res.json().get("access_token")):
            # 登录成功，存 token，跳到首页
            st.session_state.access_token = token
            st.session_state.page = "home"
            st.experimental_rerun()
        else:
            st.error("❌ 登入失敗，請檢查帳號密碼")
