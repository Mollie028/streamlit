import streamlit as st

st.set_page_config(page_title="名片辨識登入", page_icon="🔐")

# 假資料
DUMMY_USERNAME = "testuser"
DUMMY_PASSWORD = "123456"
DUMMY_ROLE = "admin"
DUMMY_TOKEN = "fake-token"

# 初始化頁面狀態
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

# ✅ 登出按鈕處理
if st.session_state.get("access_token") and st.session_state["current_page"] != "login":
    if st.button("🔓 登出"):
        st.session_state.clear()
        st.session_state["current_page"] = "login"
        st.rerun()

# ✅ 登入頁面
if st.session_state["current_page"] == "login":
    st.title("🔐 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
            st.session_state["access_token"] = DUMMY_TOKEN
            st.session_state["username"] = DUMMY_USERNAME
            st.session_state["role"] = DUMMY_ROLE
            st.session_state["current_page"] = "home"
            st.rerun()
        else:
            st.error("❌ 帳號或密碼錯誤")

# ✅ 首頁（依照身份顯示功能按鈕）
elif st.session_state["current_page"] == "home":
    st.success(f"🎉 歡迎 {st.session_state['username']}（{st.session_state['role']}）")

    if st.session_state["role"] == "admin":
        st.info("🛠️ 管理員功能")
        if st.button("📤 資料匯出"):
            st.session_state["current_page"] = "export"
            st.rerun()
        if st.button("🔐 帳號管理"):
            st.session_state["current_page"] = "accounts"
            st.rerun()
        if st.button("🗑️ 名片刪除"):
            st.session_state["current_page"] = "delete"
            st.rerun()

    st.info("📦 共用功能")
    if st.button("📷 拍照上傳名片"):
        st.session_state["current_page"] = "upload"
        st.rerun()
    if st.button("🎤 錄音語音備註"):
        st.session_state["current_page"] = "voice"
        st.rerun()
    if st.button("🔍 查詢名片紀錄"):
        st.session_state["current_page"] = "search"
        st.rerun()

# ✅ 各功能頁：你可以之後把每個功能寫進對應的區塊
elif st.session_state["current_page"] == "upload":
    st.title("📷 拍照上傳名片")
    st.write("這裡是名片上傳頁面。")
    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))

elif st.session_state["current_page"] == "voice":
    st.title("🎤 語音備註")
    st.write("這裡是語音錄音功能。")
    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))

elif st.session_state["current_page"] == "search":
    st.title("🔍 查詢紀錄")
    st.write("這裡是名片查詢頁。")
    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))

elif st.session_state["current_page"] == "accounts":
    st.title("🔐 帳號管理")
    st.write("這裡是管理員帳號功能頁。")
    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))

elif st.session_state["current_page"] == "export":
    st.title("📤 資料匯出")
    st.write("這裡是資料匯出功能頁。")
    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))

elif st.session_state["current_page"] == "delete":
    st.title("🗑️ 名片刪除")
    st.write("這裡是名片刪除功能頁。")
    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))
