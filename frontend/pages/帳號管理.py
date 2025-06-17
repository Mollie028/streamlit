import streamlit as st

def render():
    st.set_page_config(page_title="帳號管理", page_icon="🔐")
    st.header("🔐 帳號管理（限管理員）")
    st.write("這裡放「帳號管理」的介面，例如建立／刪除使用者、重設密碼")

