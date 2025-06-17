import streamlit as st
import requests

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

st.set_page_config(page_title="名片辨識系統", page_icon="📇")

# 初始化 page 狀態
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# ======================
# ⛔ 尚未登入 → 顯示登入畫面
# ======================
if not st.session_state["access_token"] or st.session_state["page"] == "login":
    st.title("🔐 請先登入")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        try:
            res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state["access_token"] = res.json().get("access_token")
                st.session_state["page"] = "home"
                st.rerun()
            else:
                st.error("❌ 登入失敗，請確認帳號密碼")
        except Exception as e:
            st.error(f"🚨 登入錯誤：{e}")
    st.stop()

# ======================
# ✅ 已登入 → 顯示首頁功能
# ======================
with st.spinner("🔐 載入使用者資料..."):
    try:
        res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {st.session_state['access_token']}"})
        user = res.json()
        username = user.get("username")
        role = user.get("role")
        st.success(f"👋 歡迎 {username}（{role}）")

        # 管理員功能
        if role == "admin":
            st.page_link("frontend/pages/名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("frontend/pages/語音備註.py", label="🎤 語音備註", icon="🎙️")
            st.page_link("frontend/pages/查詢名片紀錄.py", label="🔍 查詢紀錄", icon="🔍")
            st.page_link("frontend/pages/帳號管理.py", label="👥 帳號管理", icon="🧑")
            st.page_link("frontend/pages/資料匯出.py", label="📤 資料匯出", icon="📦")
            st.page_link("frontend/pages/名片刪除.py", label="🗑️ 名片刪除", icon="🗑️")
        else:
            st.page_link("frontend/pages/名片拍照.py", label="📷 拍照上傳名片", icon="📸")
            st.page_link("frontend/pages/語音備註.py", label="🎤 語音備註", icon="🎙️")
            st.page_link("frontend/pages/查詢名片紀錄.py", label="🔍 查詢紀錄", icon="🔍")
            st.page_link("frontend/pages/資料匯出.py", label="📤 資料匯出", icon="📦")

        if st.button("登出"):
            st.session_state.clear()
            st.rerun()

    except Exception as e:
        st.error(f"❌ 無法取得使用者資訊：{e}")
        st.stop()
