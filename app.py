import streamlit as st

# 导入所有页面
from frontend.pages import login, 首頁, 名片拍照, 語音備註, 查詢名片紀錄, 帳號管理, 資料匯出, 名片刪除

st.set_page_config(page_title="名片辨識系統", layout="centered")

# 如果还没选择过 page，就让它先去登录页
if "page" not in st.session_state:
    st.session_state.page = "login"

# 根据 session_state.page 调用对应页面的 render()
page = st.session_state.page
if page == "login":
    login.render()
elif page == "home":
    首頁.render()
elif page == "名片拍照":
    名片拍照.render()
elif page == "語音備註":
    語音備註.render()
elif page == "查詢名片紀錄":
    查詢名片紀錄.render()
elif page == "帳號管理":
    帳號管理.render()
elif page == "資料匯出":
    資料匯出.render()
elif page == "名片刪除":
    名片刪除.render()
else:
    st.error(f"找不到頁面：{page}")
