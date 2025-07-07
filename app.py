import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from services.auth_service import check_login, create_user
from core.config import API_BASE  

# ------------------------
# 設定與假資料
# ------------------------
st.set_page_config(page_title="名片辨識系統", layout="centered")
ocr_url = f"{API_BASE}/ocr"
DUMMY_USERNAME = "testuser"
DUMMY_PASSWORD = "123456"
DUMMY_ROLE = "admin"
DUMMY_TOKEN = "fake-token"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

# ------------------------
# 登出按鈕（非登入頁才顯示）
# ------------------------
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
            role = check_login(username, password)
            if role:
                st.session_state["access_token"] = "ok"
                st.session_state["username"] = username
                st.session_state["role"] = role
                st.session_state["current_page"] = "home"
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤")

    with col2:
        if st.button("註冊"):
            st.session_state["current_page"] = "register"
            st.rerun()

# ------------------------
# 首頁：依角色顯示功能
# ------------------------
elif st.session_state["current_page"] == "register":
    st.title("📝 註冊新帳號")
    new_user = st.text_input("新帳號")
    new_pass = st.text_input("新密碼", type="password")
    role = st.selectbox("角色", ["user", "admin"])

    if st.button("註冊"):
        st.toast("📡 正在送出註冊資料...")
        result = create_user(new_user, new_pass, role)

        if result is True:
            st.success("✅ 註冊成功，請回到登入頁")
        else:
            st.error(f"❌ 註冊失敗，原因：{result}")
            st.code(f"🛠️ Debug 資訊：帳號={new_user}, 角色={role}")

    if st.button("返回登入"):
        st.session_state["current_page"] = "login"
        st.rerun()

elif st.session_state["current_page"] == "home":
    role = st.session_state["role"]
    username = st.session_state["username"]
    st.success(f"🎉 歡迎 {username}（{role}）")

    # -------------------------
    # 👑 管理員首頁功能畫面
    # -------------------------
    if role == "admin":
        st.info("🛠️ 管理員功能選單")

        if st.button("📷 上傳名片"):
            st.session_state["current_page"] = "ocr"
            st.rerun()

        if st.button("🎤 錄音語音備註"):
            st.session_state["current_page"] = "voice"
            st.rerun()

        if st.button("🗂️ 帳號管理"):
            st.session_state["current_page"] = "account"
            st.rerun()

        if st.button("👥 使用者權限設定"):
            st.session_state["current_page"] = "user_manage"
            st.rerun()

        if st.button("🗑️ 名片刪除與編輯"):
            st.session_state["current_page"] = "delete_edit"
            st.rerun()

    # -------------------------
    # 🙋 一般使用者首頁功能畫面
    # -------------------------
    elif role == "user":
        st.info("📋 使用者功能選單")

        if st.button("📷 上傳名片"):
            st.session_state["current_page"] = "ocr"
            st.rerun()

        if st.button("🎤 錄音語音備註"):
            st.session_state["current_page"] = "voice"
            st.rerun()

        if st.button("🔍 查詢紀錄"):
            st.session_state["current_page"] = "query"
            st.rerun()

elif st.session_state["current_page"] == "ocr":
    import frontend.pages.ocr as ocr_page
    ocr_page.run()

elif st.session_state["current_page"] == "voice":
    import frontend.pages.語音備註 as voice_page
    voice_page.run()

elif st.session_state["current_page"] == "account":
    import frontend.pages.帳號管理 as acc_page
    acc_page.run()

elif st.session_state["current_page"] == "user_manage":
    import frontend.pages.使用者權限設定 as user_page
    user_page.run()

elif st.session_state["current_page"] == "delete_edit":
    import frontend.pages.名片刪除 as del_page
    del_page.run()

elif st.session_state["current_page"] == "query":
    import frontend.pages.查詢名片紀錄 as query_page
    query_page.run()
