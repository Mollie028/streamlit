import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from core.config import API_BASE

st.set_page_config(page_title="名片辨識系統", layout="centered")

# 初始化狀態
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

# 登出按鈕（非登入頁時顯示）
if st.session_state.get("access_token") and st.session_state["current_page"] != "login":
    if st.button("🔓 登出"):
        st.session_state.clear()
        st.session_state["current_page"] = "login"
        st.rerun()

# ------------------------
# 登入頁面
# ------------------------
if st.session_state["current_page"] == "login":
    st.title("🔐 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("登入"):
            res = requests.post(f"{API_BASE}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                result = res.json()
                st.session_state["access_token"] = result["access_token"]
                st.session_state["username"] = username
                st.session_state["role"] = result.get("role", "user")
                st.session_state["company_name"] = result.get("company_name", "")
                
                # ✅ 儲存登入使用者資訊
                st.session_state["user_info"] = {
                    "id": result.get("id"),
                    "username": username,
                    "is_admin": result.get("role", "user") == "admin"
                }

                st.session_state["current_page"] = "home"
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤")

    with col2:
        if st.button("註冊"):
            st.session_state["current_page"] = "register"
            st.rerun()

# ------------------------
# 註冊頁面
# ------------------------
elif st.session_state["current_page"] == "register":
    st.title("📝 註冊新帳號")
    new_user = st.text_input("新帳號")
    new_pass = st.text_input("新密碼", type="password")
    company_name = st.text_input("公司名稱（可留空）")
    identity = st.radio("請選擇身分", ["使用者", "管理員"], horizontal=True)
    is_admin = identity == "管理員"

    if st.button("註冊"):
        st.toast("📡 正在送出註冊資料...")
        payload = {
            "username": new_user,
            "password": new_pass,
            "company_name": company_name,
            "is_admin": is_admin
        }

        try:
            res = requests.post(f"{API_BASE}/register", json=payload)
            if res.status_code == 200:
                st.success("✅ 註冊成功，請回到登入頁")
            else:
                st.error(f"❌ 註冊失敗：{res.json().get('message')}")
        except Exception as e:
            st.error("❌ 註冊失敗，系統錯誤")
            st.code(str(e))

    if st.button("返回登入"):
        st.session_state["current_page"] = "login"
        st.rerun()

# ------------------------
# 首頁（依角色顯示功能選單）
# ------------------------
elif st.session_state["current_page"] == "home":
    role = st.session_state["role"]
    username = st.session_state["username"]
    st.success(f"🎉 歡迎 {username}（{role}）")

    if role == "admin":
        st.info("🛠️ 管理員功能選單")
        if st.button("👥 帳號管理"):
            st.session_state["current_page"] = "account_manage"
            st.rerun()
        if st.button("➕ 新增名片"):
            st.session_state["current_page"] = "add_card"
            st.rerun()
        if st.button("📂 名片清單"):
            st.session_state["current_page"] = "card_list"
            st.rerun()
    else:
        st.info("📋 使用者功能選單")
        if st.button("🔐 修改密碼"):
            st.session_state["current_page"] = "change_password"
            st.rerun()
        if st.button("➕ 新增名片"):
            st.session_state["current_page"] = "add_card"
            st.rerun()
        if st.button("📂 名片清單"):
            st.session_state["current_page"] = "card_list"
            st.rerun()

# ------------------------
# 各功能頁面導向
# ------------------------

elif st.session_state["current_page"] == "account_manage":
    from frontend.pages import account_manager
    account_manager.run()

elif st.session_state["current_page"] == "add_card":
    from frontend.pages import add_card
    add_card.run()

elif st.session_state["current_page"] == "card_list":
    from frontend.pages import card_list
    card_list.run()

elif st.session_state["current_page"] == "change_password":
    from frontend.pages import change_password
    change_password.run()







