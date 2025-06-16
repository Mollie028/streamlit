import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="首頁", page_icon="🔐")

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 如果已登入，就自動跳到「首頁」
if st.session_state.get("access_token"):
    switch_page("首頁")
    st.stop()

# ✅ 顯示登入表單
st.title("🔐 請先登入")
username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200:
            access_token = res.json().get("access_token")
            st.session_state["access_token"] = access_token
            st.success("✅ 登入成功，導向首頁...")
            switch_page("首頁")  # ✅ 中文標題
        else:
            st.error("❌ 登入失敗，請檢查帳密")
    except Exception as e:
        st.error(f"🚨 登入錯誤：{e}")
 
