import streamlit as st
import requests

st.set_page_config(page_title="名片辨識登入", page_icon="🔐")

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 已登入就顯示按鈕
if st.session_state.get("access_token"):
    st.success("✅ 登入成功，請點下方進入首頁")
    st.page_link("首頁", label="👉 前往首頁", icon="🏠")
    st.stop()

# ✅ 登入畫面
st.title("🔐 名片辨識系統登入")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json().get("access_token")
            if token:
                st.session_state["access_token"] = token
                st.success("✅ 登入成功，請點下方進入首頁")
                st.page_link("首頁", label="👉 前往首頁", icon="🏠")
            else:
                st.error("❌ 沒有回傳 access_token")
        else:
            st.error("❌ 登入失敗，請確認帳密")
    except Exception as e:
        st.error(f"🚨 登入錯誤：{e}")
