import streamlit as st
import requests

# ✅ 後端 API URL
API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 畫面設定
st.set_page_config(page_title="名片辨識登入", page_icon="🔐")

# ✅ 如果已經登入就自動導向首頁
if st.session_state.get("access_token"):
    st.switch_page("首頁")  # ✅ 頁面標題要 match 頁面 .py 的 set_page_config
    st.stop()

# ✅ 登入頁面內容
st.title("🔐 請先登入")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200:
            access_token = res.json().get("access_token")
            if access_token:
                st.session_state["access_token"] = access_token
                st.success("✅ 登入成功，正在導向首頁...")
                st.rerun()  
            else:
                st.error("❌ 後端未傳回 access_token")
        else:
            st.error("❌ 登入失敗，請檢查帳號密碼")
    except Exception as e:
        st.error(f"🚨 無法登入：{e}")
