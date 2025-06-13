import streamlit as st
import requests

st.set_page_config(page_title="登入後首頁", page_icon="🏠")

# 取得登入後儲存的 access_token
access_token = st.session_state.get("access_token", None)

# 如果尚未登入，導回主頁
if not access_token:
    st.warning("⚠️ 尚未登入，請回到主頁")
    st.stop()

# 呼叫 /me API 取得使用者資訊
with st.spinner("🔐 讀取使用者資料中..."):
    try:
        response = requests.get(
            "https://ocr-whisper-api-production-03e9.up.railway.app/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        user = response.json()
        username = user.get("username")
        role = user.get("role")

        st.session_state["role"] = role  # 存下角色供其他頁使用

        st.success(f"👤 歡迎登入：{username}")

        # 顯示管理員功能區塊
        if role == "admin":
            st.info("🛠️ 管理員功能")
            st.write("🔐 帳號管理")
            st.write("📤 資料匯出")
            st.write("🗑️ 名片刪除")

        # 顯示一般使用者功能區塊
        else:
            st.info("🧑‍💻 一般使用者功能")
            st.write("📷 拍照上傳名片")
            st.write("🎤 錄音語音備註")
            st.write("🔍 名片查詢")

    except Exception as e:
        st.error(f"❌ 無法取得使用者資訊：{e}")
        st.stop()
