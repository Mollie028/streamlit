import streamlit as st

st.set_page_config(page_title="名片辨識登入", page_icon="🔐")

# ✅ 模擬帳號資料（寫死帳號密碼與角色）
DUMMY_USERNAME = "testuser"
DUMMY_PASSWORD = "123456"
DUMMY_ROLE = "admin"
DUMMY_TOKEN = "fake-token"

# ✅ 已登入畫面（根據角色顯示功能）
if st.session_state.get("access_token") and st.session_state.get("role"):
    username = st.session_state.get("username")
    role = st.session_state.get("role")
    st.success(f"🎉 歡迎 {username}（{role}）")

    if role == "admin":
        st.info("🛠️ 管理員功能")
        st.button("📤 資料匯出")
        st.button("🔐 帳號管理")
        st.button("🗑️ 名片刪除")
        st.button("📷 拍照上傳名片")
        st.button("🎤 錄音語音備註")
        st.button("🔍 查詢名片紀錄")
    else:
        st.info("🧑‍💻 一般使用者功能")
        st.button("📷 拍照上傳名片")
        st.button("🎤 錄音語音備註")
        st.button("🔍 查詢名片紀錄")

    if st.button("🔓 登出"):
        st.session_state.clear()
        st.rerun()

    st.stop()

# ✅ 尚未登入
st.title("🔐 登入系統")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
        st.session_state["access_token"] = DUMMY_TOKEN
        st.session_state["username"] = DUMMY_USERNAME
        st.session_state["role"] = DUMMY_ROLE
        st.success("✅ 登入成功，重新導向中...")
        st.rerun()
    else:
        st.error("❌ 帳號或密碼錯誤")
