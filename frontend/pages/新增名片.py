import streamlit as st
import requests
from core.config import API_BASE
from components.auth import is_logged_in, logout_button

# ===================== ☁️ 登入狀態區塊 =====================
if not is_logged_in():
    st.error("請先登入")
    st.stop()

# ===================== 🔐 登出按鈕 =====================
logout_button()

# ===================== 🙋‍♀️ 歡迎訊息 =====================
username = st.session_state.get("username", "")
role = st.session_state.get("role", "")
st.success(f"🎉 歡迎 {username}（{role}）")

# ===================== 🔘 選單按鈕 =====================
if role == "admin":
    st.subheader("🛠 管理員功能選單")

    if st.button("👥 帳號管理"):
        st.session_state["current_page"] = "account"
    if st.button("🆕 新增名片"):
        st.session_state["current_page"] = "add_card"
    if st.button("📇 名片清單"):
        st.session_state["current_page"] = "card_list"

elif role == "user":
    st.subheader("🧰 使用者功能選單")

    if st.button("🔑 修改密碼"):
        st.session_state["current_page"] = "change_password"
    if st.button("🆕 新增名片"):
        st.session_state["current_page"] = "add_card"
    if st.button("📇 名片清單"):
        st.session_state["current_page"] = "card_list"

# ===================== 📄 頁面顯示邏輯 =====================
if "current_page" in st.session_state:
    if st.session_state["current_page"] == "account":
        import frontend.pages.帳號管理 as acc_page
        acc_page.run()

    elif st.session_state["current_page"] == "add_card":
        import frontend.pages.新增名片 as add_page
        add_page.run()

    elif st.session_state["current_page"] == "card_list":
        import frontend.pages.名片清單 as card_page
        card_page.run()

    elif st.session_state["current_page"] == "change_password":
        import frontend.pages.修改密碼 as pw_page
        pw_page.run()
