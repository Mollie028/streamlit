import streamlit as st
import requests

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

def render():
    st.set_page_config(page_title="首頁", page_icon="🏠")
    # 檢查是否登入
    token = st.session_state.get("access_token")
    if not token:
        st.warning("⚠️ 尚未登入")
        st.stop()

    # 取 /me
    res = requests.get(
        f"{API_BASE}/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if res.status_code != 200:
        st.error("❌ 取得使用者資訊失敗")
        st.stop()

    user = res.json()
    username = user.get("username", "")
    role     = user.get("role", "")

    st.success(f"👤 歡迎：{username}（{role}）")

    # 管理員功能
    if role == "admin":
        st.info("🛠️ 管理員功能")
        if st.button("📷 拍照上傳名片"):
            st.session_state.page = "名片拍照"; st.experimental_rerun()
        if st.button("🎤 錄音語音備註"):
            st.session_state.page = "語音備註"; st.experimental_rerun()
        if st.button("🔍 查詢名片紀錄"):
            st.session_state.page = "查詢名片紀錄"; st.experimental_rerun()
        if st.button("🔐 帳號管理"):
            st.session_state.page = "帳號管理"; st.experimental_rerun()
        if st.button("📤 資料匯出"):
            st.session_state.page = "資料匯出"; st.experimental_rerun()
        if st.button("🗑️ 名片刪除"):
            st.session_state.page = "名片刪除"; st.experimental_rerun()

    # 一般使用者功能
    else:
        st.info("🧑‍💻 一般使用者功能")
        if st.button("📷 拍照上傳名片"):
            st.session_state.page = "名片拍照"; st.experimental_rerun()
        if st.button("🎤 錄音語音備註"):
            st.session_state.page = "語音備註"; st.experimental_rerun()
        if st.button("🔍 查詢名片紀錄"):
            st.session_state.page = "查詢名片紀錄"; st.experimental_rerun()
