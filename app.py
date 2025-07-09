import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from services.auth_service import check_login, create_user
from core.config import API_BASE  

st.set_page_config(page_title="名片辨識系統", layout="centered")
ocr_url = f"{API_BASE}/ocr"

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
# 註冊頁面（已新增 is_admin 選項）
# ------------------------
elif st.session_state["current_page"] == "register":
    st.title("📝 註冊新帳號")
    
    # 📌 這些是表單欄位（都要寫在 button 外）
    new_user = st.text_input("新帳號")
    new_pass = st.text_input("新密碼", type="password")
    company_name = st.text_input("公司名稱（可留空）")
    identity = st.radio("請選擇身分", ["使用者", "管理員"], horizontal=True)
    is_admin = identity == "管理員"  # ✅ 判斷布林值

    # 📌 寫在 button 裡的：送出 payload
    if st.button("註冊"):
        st.toast("📡 正在送出註冊資料...")

        payload = {
            "username": new_user,
            "password": new_pass,
            "company_name": company_name,
            "is_admin": is_admin  # ✅ 傳出去的布林值
        }

        try:
            res = requests.post(f"{API_BASE}/register", json=payload)
            if res.status_code == 200:
                st.success("✅ 註冊成功，請回到登入頁")
            else:
                st.error(f"❌ 註冊失敗，原因：{res.json().get('message')}")
                st.code(f"🛠️ Debug 資訊：{res.text}")
        except Exception as e:
            st.error("❌ 註冊失敗，系統錯誤")
            st.code(str(e))

    if st.button("返回登入"):
        st.session_state["current_page"] = "login"
        st.rerun()


# ------------------------
# 首頁畫面（依身分顯示功能）
# ------------------------
elif st.session_state["current_page"] == "home":
    role = st.session_state["role"]
    username = st.session_state["username"]
    st.success(f"🎉 歡迎 {username}（{role}）")

    if role == "admin":
        st.info("🛠️ 管理員功能選單")
        if st.button("📷 上傳名片"):
            st.session_state["current_page"] = "ocr"
            st.rerun()
        if st.button("🎤 錄音語音備註"):
            st.session_state["current_page"] = "voice"
            st.rerun()
        if st.button("修改密碼"):
            st.session_state["current_page"] = "account"
            st.rerun()
        if st.button("👥 使用者權限設定"):
            st.session_state["current_page"] = "user_manage"
            st.rerun()
        if st.button("🗑️ 名片刪除與編輯"):
            st.session_state["current_page"] = "delete_edit"
            st.rerun()
    else:
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
        if st.button("修改密碼"):
            st.session_state["current_page"] = "account"
            st.rerun()

# ------------------------
# 各功能頁面分流
# ------------------------
elif st.session_state["current_page"] == "ocr":
    import frontend.pages.ocr as ocr_page
    ocr_page.run()

elif st.session_state["current_page"] == "voice":
    import frontend.pages.語音備註 as voice_page
    voice_page.run()

elif st.session_state["current_page"] == "account":
    import frontend.pages.修改密碼 as acc_page
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
