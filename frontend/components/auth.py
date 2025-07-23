import streamlit as st

def is_logged_in():
    """檢查是否登入，並回傳登入資訊（username, token, is_admin）"""
    if "token" in st.session_state and "username" in st.session_state:
        return {
            "username": st.session_state["username"],
            "token": st.session_state["token"],
            "is_admin": st.session_state.get("is_admin", False),
        }
    else:
        return None

def logout_button():
    """畫面右上角顯示登出按鈕"""
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 登出"):
        st.session_state.clear()
        st.success("已登出，請重新登入")
        st.rerun()
