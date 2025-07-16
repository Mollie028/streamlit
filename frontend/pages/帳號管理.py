import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

API_BASE_URL = "https://ocr-whisper-production-2.up.railway.app"

def main():
    st.set_page_config(page_title="帳號管理", page_icon="👤", layout="wide")

    st.markdown("""
        <style>
        .ag-theme-streamlit .ag-root-wrapper {
            height: 380px !important;
            width: 95% !important;
            margin: auto;
        }
        .ag-header-cell-label, .ag-cell {
            justify-content: center;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 👤 帳號清單")

    @st.cache_data
    def get_users():
        ...
        # ✅ 這裡保留不變

    users = get_users()
    ...
    # ✅ 這邊照你的邏輯縮排進 main() 函式

    if st.button("🔙 返回主頁"):
        st.switch_page("app.py")  # 或你要跳的頁面

# ✅ 保留 run() 給 app.py 呼叫
def run():
    main()
