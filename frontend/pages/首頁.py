import streamlit as st
import requests

st.set_page_config(page_title="Home", page_icon="🏠")

# 取得登入後儲存的 access_token
access_token = st.session_state.get("access_token", None)
if not access_token:
    st.warning("⚠️ 尚未登入，請回到主頁")
    st.stop()

# 呼叫 /me API 取得使用者資訊
with st.spinner("🔐 讀取使用者資料中..."):
    try:
        response = requests.get(
            "https://ocr-whisper-api-production-03e9.up.railway.app/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        user = response.json()
        username = user.get("username")
        role = user.get("role")

        st.session_state["role"] = role  # 存下角色供其他頁使用
        st.session_state["username"] = username

        st.success(f"👤 歡迎登入：{username}（{role}）")

        # 顯示管理員功能區塊
        if role == "admin":
            st.info("🛠️ 管理員功能")
            st.page_link("pages/名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("pages/語音備註.py", label="🎤 錄音語音備註", icon="🎙️")
            st.page_link("pages/查詢名片紀錄.py", label="🔍 查詢名片紀錄", icon="🔍")
            st.page_link("pages/帳號管理.py", label="🔐 帳號管理", icon="🧑")
            st.page_link("pages/資料匯出.py", label="📤 資料匯出", icon="📦")
            st.page_link("pages/名片刪除.py", label="🗑️ 名片刪除", icon="🗑️")

        # 顯示一般使用者功能區塊
        else:
            st.info("🧑‍💻 一般使用者功能")
            st.page_link("pages/名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("pages/語音備註.py", label="🎤 錄音語音備註", icon="🎙️")
            st.page_link("pages/查詢名片紀錄.py", label="🔍 查詢名片紀錄", icon="🔍")

    except Exception as e:
        st.error(f"❌ 無法取得使用者資訊：{e}")
        st.stop()
