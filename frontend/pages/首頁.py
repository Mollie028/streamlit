# frontend/pages/首頁.py
import streamlit as st

st.set_page_config(page_title="首頁", page_icon="🏠")

if "access_token" not in st.session_state:
    st.warning("請先登入")
    st.stop()

username = st.session_state.get("username", "未知使用者")
role = st.session_state.get("role", "user")

st.success(f"👋 歡迎 {username}（{role}）")

# ✅ 管理員功能區塊
if role == "admin":
    st.info("🛠️ 管理員功能")
    st.page_link("名片拍照.py", label="📷 拍照上傳名片")
    st.page_link("語音備註.py", label="🎤 語音備註")
    st.page_link("帳號管理.py", label="🔐 帳號管理")
    st.page_link("資料匯出.py", label="📤 資料匯出")
    st.page_link("名片刪除.py", label="🗑️ 名片刪除")

# ✅ 一般使用者功能區塊
else:
    st.info("🧑‍💻 一般使用者功能")
    st.page_link("名片拍照.py", label="📷 拍照上傳名片")
    st.page_link("語音備註.py", label="🎤 語音備註")
    st.page_link("資料匯出.py", label="📤 資料匯出")
