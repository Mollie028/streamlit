import streamlit as st
import requests
from core.config import API_BASE

st.set_page_config(page_title="名片辨識系統", layout="centered")

# 初始化狀態
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

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
            try:
                res = requests.post(f"{API_BASE}/login", json={"username": username, "password": password})
                if res.status_code == 200:
                    result = res.json()
                    st.session_state["access_token"] = result["access_token"]
                    st.session_state["username"] = username
                    st.session_state["role"] = result.get("role", "user")
                    st.session_state["company_name"] = result.get("company_name", "")

                    st.session_state["user_info"] = {
                        "id": result.get("id"),
                        "username": username,
                        "is_admin": result.get("role", "user") == "admin"
                    }

                    st.session_state["user"] = {
                        "id": result.get("id"),
                        "username": username,
                        "role": result.get("role", "user")
                    }

                    st.session_state["current_page"] = "home"
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤")
            except Exception as e:
                st.error("❌ 系統錯誤，請稍後再試")
                st.code(str(e))

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
# 首頁功能選單（依角色顯示）
# ------------------------
elif st.session_state["current_page"] == "home":
    role = st.session_state.get("role", "user")
    username = st.session_state.get("username", "")
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
# 各功能導向（延遲載入）
# ------------------------
elif st.session_state["current_page"] == "account_manage":
    import importlib
    acc_page = importlib.import_module("frontend.pages.account_manager")
    acc_page.run()

elif st.session_state["current_page"] == "add_card":
    import importlib
    add_page = importlib.import_module("frontend.pages.add_card")
    add_page.run()

elif st.session_state["current_page"] == "card_list":
    import importlib
    card_page = importlib.import_module("frontend.pages.card_list")
    card_page.run()

elif st.session_state["current_page"] == "change_password":
    import importlib
    change_page = importlib.import_module("frontend.pages.change_password")
    change_page.run()
