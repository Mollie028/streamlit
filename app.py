# app.py
import streamlit as st

# ❶ 全站只呼叫一次，最一開始就設
st.set_page_config(page_title="名片辨識系統", layout="centered")

# ❷ import 各頁的 render() 函數
from frontend.pages import (
    login,
    首頁,
    名片拍照,
    語音備註,
    查詢名片紀錄,
    帳號管理,
    資料匯出,
    名片刪除,
)

# ❸ 初始化頁面指標
if "page" not in st.session_state:
    st.session_state.page = "login"

# ❹ 根據 session_state.page，執行對應的 render()
if st.session_state.page == "login":
    login.render()
elif st.session_state.page == "首頁":
    首頁.render()
elif st.session_state.page == "名片拍照":
    名片拍照.render()
elif st.session_state.page == "語音備註":
    語音備註.render()
elif st.session_state.page == "查詢名片紀錄":
    查詢名片紀錄.render()
elif st.session_state.page == "帳號管理":
    帳號管理.render()
elif st.session_state.page == "資料匯出":
    資料匯出.render()
elif st.session_state.page == "名片刪除":
    名片刪除.render()
else:
    st.error(f"Unknown page: {st.session_state.page}")
