import streamlit as st

def render():
    st.set_page_config(page_title="資料匯出", page_icon="📤")
    st.header("📤 資料匯出（限管理員）")
    st.write("這裡放「資料匯出」的介面，例如匯出名片紀錄 CSV／Excel")
