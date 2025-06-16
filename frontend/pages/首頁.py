import streamlit as st
import requests

st.set_page_config(page_title="首頁", page_icon="🏠")

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 沒有登入就跳回主頁
access_token = st.session_state.get("access_token", None)
if not access_token:
    st.warning("⚠️ 尚未登入，請回到主頁")
    st.stop()

# ✅ 呼叫後端 /me API 取得角色
with st.spinner("🔐 載入中..."):
    try:
        res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {access_token}"})
        res.raise_for_status()
        user = res.json()
        username = user.get("username")
        role = user.get("role")

        st.session_state["username"] = username
        st.session_state["role"] = role

        st.success(f"👤 歡迎：{username}（{role}）")

        if role == "admin":
            st.info("🛠️ 管理員功能")
            st.page_link("名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("語音備註.py", label="🎤 錄音語音備註", icon="🎙️")
            st.page_link("查詢名片紀錄.py", label="🔍 查詢名片紀錄", icon="🔍")
            st.page_link("帳號管理.py", label="🔐 帳號管理", icon="🧑")
            st.page_link("資料匯出.py", label="📤 資料匯出", icon="📦")
            st.page_link("名片刪除.py", label="🗑️ 名片刪除", icon="🗑️")
        else:
            st.info("🧑‍💻 一般使用者功能")
            st.page_link("名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("語音備註.py", label="🎤 錄音語音備註", icon="🎙️")
            st.page_link("查詢名片紀錄.py", label="🔍 查詢名片紀錄", icon="🔍")

    except Exception as e:
        st.error(f"❌ 無法讀取使用者資料：{e}")
