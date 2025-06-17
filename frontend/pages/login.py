# login.py 裡 render()
import streamlit as st
import requests

def render():
    st.set_page_config(page_title="登入", page_icon="🔐")
    st.title("🔐 請先登入")

    user = st.text_input("帳號")
    pwd  = st.text_input("密碼", type="password")
    if st.button("登入"):
        res = requests.post(f"{API_BASE}/login", json={"username": user, "password": pwd})
        if res.status_code == 200:
            st.session_state.access_token = res.json()["access_token"]
            # 切換到首頁
            st.session_state.page = "首頁"
            st.experimental_rerun()
        else:
            st.error("❌ 登入失敗")

