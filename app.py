import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

# ------------------------
# 設定與假資料
# ------------------------
st.set_page_config(page_title="名片辨識系統", layout="centered")
API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"
DUMMY_USERNAME = "testuser"
DUMMY_PASSWORD = "123456"
DUMMY_ROLE = "admin"
DUMMY_TOKEN = "fake-token"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

# ------------------------
# 登出按鈕（非登入頁才顯示）
# ------------------------
if st.session_state.get("access_token") and st.session_state["current_page"] != "login":
    if st.button("🔓 登出"):
        st.session_state.clear()
        st.session_state["current_page"] = "login"
        st.rerun()

# ------------------------
# 登入頁面
# ------------------------
if st.session_state["current_page"] == "login":
    st.title("🔐 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
            st.session_state["access_token"] = DUMMY_TOKEN
            st.session_state["username"] = DUMMY_USERNAME
            st.session_state["role"] = DUMMY_ROLE
            st.session_state["current_page"] = "home"
            st.rerun()
        else:
            st.error("❌ 帳號或密碼錯誤")

# ------------------------
# 首頁：依角色顯示功能
# ------------------------
elif st.session_state["current_page"] == "home":
    st.success(f"🎉 歡迎 {st.session_state['username']}（{st.session_state['role']}）")

    st.info("🛠️ 功能選單")
    if st.button("上傳名片"):
        st.session_state["current_page"] = "ocr"
        st.rerun()
    if st.button("錄音語音備註"):
        st.session_state["current_page"] = "voice"
        st.rerun()
elif st.session_state["current_page"] == "ocr":
    st.write("🧭 現在進入 ocr 頁面")
    import frontend.pages.ocr as ocr_page
    ocr_page.run()

elif st.session_state["current_page"] == "voice":
    import pages.語音備註 as voice_page
    voice_page.run()
    


