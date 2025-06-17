import streamlit as st
import requests

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

def render():
    st.title("🔐 請先登入")
    user = st.text_input("帳號")
    pwd  = st.text_input("密碼", type="password")
    if st.button("登入"):
        try:
            r = requests.post(f"{API_BASE}/login",
                              json={"username": user, "password": pwd})
            if r.status_code == 200 and (token := r.json().get("access_token")):
                st.session_state.access_token = token
                # 登录成功后直接跳到首页
                st.session_state.page = "home"
                st.experimental_rerun()
            else:
                st.error("❌ 帳密錯誤或後端未回傳 token")
        except Exception as e:
            st.error(f"🚨 登入失敗：{e}")
