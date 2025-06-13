import streamlit as st
import requests

st.set_page_config(page_title="登入後首頁", page_icon="🏠")

# 讀取登入時儲存的 access_token
access_token = st.session_state.get("access_token", None)

if not access_token:
    st.warning("⚠️ 尚未登入，請回到主頁")
    st.stop()

# 呼叫 /me 取得使用者資訊
with st.spinner("🔐 讀取使用者資料中..."):
    try:
        response = requests.get(
            "https://ocr-whisper-api-production-03e9.up.railway.app/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user = response.json()
        st.success(f"👤 歡迎登入：{user['username']}")

        # 🎯 TODO：根據角色顯示對應頁面
        if user.get("username") == "admin":
            st.info("🔧 管理員功能區塊")
            st.write("✅ 帳號管理、刪除功能、匯出功能等")
        else:
            st.info("🧑‍💻 一般使用者功能區")
            st.write("🔍 可使用查詢、拍照、語音備註...")

    except Exception as e:
        st.error(f"無法讀取使用者資訊：{e}")
