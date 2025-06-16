import streamlit as st
import requests

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"
st.set_page_config(page_title="登入", layout="centered")

# ✅ 如果已經登入，自動跳轉首頁
if st.session_state.get("access_token"):
    st.switch_page("pages/Home.py")

st.title("🔐 請先登入")
user = st.text_input("帳號")
pwd = st.text_input("密碼", type="password")

if st.button("登入"):
    res = requests.post(f"{API_BASE}/login", json={"username": user, "password": pwd})
    if res.status_code == 200:
        token = res.json()["access_token"]
        st.session_state["access_token"] = token

        # 🔍 再呼叫 /me 拿 role 與 username
        me = requests.get(
            f"{API_BASE}/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if me.status_code == 200:
            user_info = me.json()
            st.session_state["username"] = user_info.get("username", "")
            st.session_state["role"] = user_info.get("role", "")

            st.success("✅ 登入成功，正在導向...")
            st.rerun()  
        else:
            st.error("❌ 無法取得使用者資訊")
    else:
        st.error("❌ 登入失敗，請確認帳密是否正確")
