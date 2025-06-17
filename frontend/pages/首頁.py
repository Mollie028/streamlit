import streamlit as st
import requests

st.set_page_config(page_title="首頁", page_icon="🏠")

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

access_token = st.session_state.get("access_token", None)
if not access_token:
    st.warning("⚠️ 尚未登入，請回登入頁")
    st.stop()

# 取得角色
with st.spinner("🔐 載入使用者資訊中..."):
    try:
        res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {access_token}"})
        user = res.json()
        username = user.get("username")
        role = user.get("role")

        st.session_state["username"] = username
        st.session_state["role"] = role

        st.success(f"👤 歡迎登入：{username}（{role}）")

        if role == "admin":
            st.page_link("名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("語音備註.py", label="🎤 語音備註", icon="🎙️")
            st.page_link("查詢名片紀錄.py", label="🔍 查詢紀錄", icon="🔍")
            st.page_link("帳號管理.py", label="🔐 帳號管理", icon="👥")
            st.page_link("資料匯出.py", label="📤 匯出資料", icon="📦")
            st.page_link("名片刪除.py", label="🗑️ 刪除名片", icon="🗑️")
        else:
            st.page_link("名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("語音備註.py", label="🎤 語音備註", icon="🎙️")
            st.page_link("查詢名片紀錄.py", label="🔍 查詢紀錄", icon="🔍")

    except Exception as e:
        st.error(f"❌ 無法取得角色資訊：{e}")
        st.stop()
