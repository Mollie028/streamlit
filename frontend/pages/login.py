import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="登入頁面", page_icon="🔐")  

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

# 如果已經登入就直接跳轉首頁
if st.session_state.get("access_token"):
    switch_page("首頁")

st.title("🔐 登入系統")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json().get("access_token")
            if token:
                st.session_state["access_token"] = token
                st.success("✅ 登入成功，正在導向首頁...")
                switch_page("首頁")  # ✅ 對應到 pages/首頁.py
            else:
                st.error("❌ 後端沒有傳回 access_token")
        else:
            st.error("❌ 登入失敗，請確認帳號密碼")
    except Exception as e:
        st.error(f"🚨 登入錯誤：{e}")

