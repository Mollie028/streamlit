import streamlit as st
import requests

st.set_page_config(page_title="首頁", page_icon="🏠")

# ✅ 驗證登入狀態
access_token = st.session_state.get("access_token")
if not access_token:
    st.warning("⚠️ 尚未登入，請回到主頁")
    st.stop()

# ✅ 呼叫 /me API 拿角色資訊
try:
    res = requests.get(
        "https://ocr-whisper-api-production-03e9.up.railway.app/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    res.raise_for_status()
    user = res.json()
    role = user.get("role", "user")
    username = user.get("username")
    st.session_state["role"] = role
    st.session_state["username"] = username
except Exception as e:
    st.error(f"❌ 無法取得使用者資料：{e}")
    st.stop()

# ✅ 顯示歡迎語
st.success(f"👋 歡迎登入：{username}（身份：{role}）")

# ✅ 根據身份顯示功能
if role == "admin":
    st.info("🛠️ 管理員功能區")
    st.page_link("名片拍照.py", label="📷 拍照上傳名片")
    st.page_link("語音備註.py", label="🎤 語音備註")
    st.page_link("查詢名片紀錄.py", label="🔍 查詢紀錄")
    st.page_link("帳號管理.py", label="🔐 帳號管理")
    st.page_link("名片刪除.py", label="🗑️ 名片刪除")
    st.page_link("資料匯出.py", label="📤 資料匯出")
else:
    st.info("🧑‍💻 一般使用者功能區")
    st.page_link("名片拍照.py", label="📷 拍照上傳名片")
    st.page_link("語音備註.py", label="🎤 語音備註")
    st.page_link("查詢名片紀錄.py", label="🔍 查詢紀錄")
