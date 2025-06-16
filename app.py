import streamlit as st
import requests

# ✅ API
API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 頁面設定
st.set_page_config(page_title="名片辨識系統", layout="centered")

# ✅ 已登入就導向首頁按鈕
if st.session_state.get("access_token"):
    st.success("✅ 已登入，請點下方按鈕前往首頁")
    st.page_link("首頁", label="👉 前往首頁", icon="🏠")
    st.stop()

# ✅ 尚未登入：顯示登入畫面
st.title("🔐 請先登入")
user = st.text_input("帳號")
pwd = st.text_input("密碼", type="password")

if st.button("登入"):
    res = requests.post(
        f"{API_BASE}/login",
        json={"username": user, "password": pwd}
    )
    if res.status_code == 200:
        st.session_state.access_token = res.json()["access_token"]
        st.success("✅ 登入成功，請點下方按鈕進入首頁")
        st.page_link("首頁", label="👉 前往首頁", icon="🏠")
    else:
        st.error("❌ 登入失敗，請確認帳密是否正確")
