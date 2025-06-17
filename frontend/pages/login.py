import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

# ✅ 頁面設定
st.set_page_config(page_title="登入系統", page_icon="🔐")

# ✅ 後端 API URL（請改成你的 Railway API）
API_URL = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ✅ 如果已經登入就導回首頁
if st.session_state.get("access_token"):
    switch_page("首頁")

# ✅ 登入表單
st.title("🔐 登入系統")

username = st.text_input("帳號")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    try:
        # 1️⃣ 呼叫 /login API
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            access_token = res.json().get("access_token")
            if not access_token:
                st.error("❌ 後端未回傳 access_token")
                st.stop()

            # ✅ 存下 access_token
            st.session_state["access_token"] = access_token

            # 2️⃣ 呼叫 /me API，取得使用者資訊
            me_res = requests.get(
                f"{API_URL}/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if me_res.status_code == 200:
                user = me_res.json()
                st.session_state["username"] = user.get("username")
                st.session_state["role"] = user.get("role")

                st.success(f"🎉 登入成功！歡迎 {user.get('username')}（{user.get('role')}）")
                st.info("正在導向首頁...")
                switch_page("首頁")  # ✅ 導向首頁頁面（首頁.py）
            else:
                st.error("❌ 無法取得使用者資訊")
        else:
            st.error("❌ 登入失敗，請檢查帳號密碼")
    except Exception as e:
        st.error(f"🚨 登入錯誤：{e}")


