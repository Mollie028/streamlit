import streamlit as st

# 把所有页面都 import 进来
from frontend.pages import login, home, 名片拍照, 語音備註, 查詢名片紀錄, 帳號管理, 資料匯出, 名片刪除

st.set_page_config("名片辨識系統", "🏷️", layout="centered")

# 1. 如果还没登录 → 直接渲染 login 页面
if "access_token" not in st.session_state:
    login.render()
    st.stop()

# 2. 如果登录了但没有指定 page → 自动跳到 home
if "page" not in st.session_state:
    st.session_state.page = "home"
    # rerun 让下面的逻辑生效
    st.experimental_rerun()

# 3. 分发到各个页面
page = st.session_state.page
if page == "home":
    home.render()
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

