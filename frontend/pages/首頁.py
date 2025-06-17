import streamlit as st
import requests

API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

st.set_page_config(page_title="名片辨識登入", page_icon="🔐")

# ✅ 登入後，顯示首頁（依照角色）
if st.session_state.get("access_token") and st.session_state.get("role"):
    username = st.session_state.get("username")
    role = st.session_state.get("role")
    st.success(f"🎉 歡迎 {username}（{role}）")

    if role == "admin":
        st.write("🛠️ 管理員功能：資料匯出、帳號管理、名片刪除...")
    else:
        st.write("🧑‍💻 一般使用者功能：上傳名片、語音備註...")

    st.button("🔓 登出", on_click=lambda: st.session_state.clear())
    st.stop()

# ✅ 尚未登入
st.title("🔐 登入系統")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json().get("access_token")
            st.session_state["access_token"] = token

            me_res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {token}"})
            me_data = me_res.json()
            st.session_state["username"] = me_data.get("username")
            st.session_state["role"] = me_data.get("role")
            st.rerun()
        else:
            st.error("❌ 帳密錯誤，請重試")
    except Exception as e:
        st.error(f"❌ 登入失敗：{e}")
