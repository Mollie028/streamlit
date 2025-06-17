import streamlit as st
import requests

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

def render():
    st.set_page_config(page_title="首頁", page_icon="🏠")
    token = st.session_state.access_token
    r = requests.get(f"{API_BASE}/me", headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    user = r.json()

    st.success(f"👤 歡迎登入：{user['username']} （{user['role']}）")

    # 角色分流
    if user["role"] == "admin":
        st.subheader("🛠️ 管理員功能")
        if st.button("帳號管理"):
            st.session_state.page = "帳號管理"; st.experimental_rerun()
        if st.button("資料匯出"):
            st.session_state.page = "資料匯出"; st.experimental_rerun()
        if st.button("名片刪除"):
            st.session_state.page = "名片刪除"; st.experimental_rerun()

        st.markdown("---")

    st.subheader("📋 功能選單")
    if st.button("拍照上傳名片"):
        st.session_state.page = "名片拍照"; st.experimental_rerun()
    if st.button("錄音語音備註"):
        st.session_state.page = "語音備註"; st.experimental_rerun()
    if st.button("查詢名片紀錄"):
        st.session_state.page = "查詢名片紀錄"; st.experimental_rerun()
