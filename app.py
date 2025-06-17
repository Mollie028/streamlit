import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="登入", page_icon="🔐")

API = "https://ocr-whisper-api-production-03e9.up.railway.app"

if st.session_state.get("access_token"):
    switch_page("首頁")

st.title("🔐 登入系統")
username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(f"{API}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json().get("access_token")
            if token:
                st.session_state["access_token"] = token
                switch_page("首頁")
            else:
                st.error("❌ 後端未回傳 token")
        else:
            st.error("❌ 登入失敗")
    except Exception as e:
        st.error(f"🚨 登入錯誤：{e}")
