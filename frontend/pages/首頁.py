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
        st.success(f"歡迎登入：{user['username']}")

    if user.get("role") == "admin":
        st.success("管理員登入成功")
        # 顯示管理功能
        st.page_link("pages/帳戶管理.py", label="帳戶管理", icon="🛠️")
        st.page_link("pages/資料匯出.py", label="📤 資料匯出")
        # 其他 admin 專屬功能
    
    else:
        st.info("一般使用者登入成功")
        st.page_link("pages/名片拍照.py", label="📷 名片拍照")
        st.page_link("pages/語音備註.py", label="🎤 語音備註")
        st.page_link("pages/結果回顧.py", label="📖 結果回顧")


    except Exception as e:
        st.error(f"無法讀取使用者資訊：{e}")
