import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

API_BASE_URL = "https://ocr-whisper-production-2.up.railway.app"

st.set_page_config(page_title="帳號管理", page_icon="🐵", layout="wide")
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

col1, col2 = st.columns([1, 5])
with col1:
    st.download_button("⬇️ 匯出帳號清單 (CSV)", data="", file_name="users.csv", disabled=True)
with col2:
    st.markdown("## 🐵 帳號清單")

@st.cache_data
def get_users():
    try:
        res = requests.get(f"{API_BASE_URL}/users")
        if res.status_code == 200:
            return res.json()
        else:
            st.error("無法取得使用者資料。")
            return []
    except Exception as e:
        st.error("連線錯誤：" + str(e))
        return []

def main():
    users = get_users()

    if not users:
        st.stop()

    # 欄位處理
    for user in users:
        user['is_admin'] = bool(user['is_admin'])
        user['is_active'] = "啟用中" if user['is_active'] else "已停用"

    user_df = pd.DataFrame(users)

    gb = GridOptionsBuilder.from_dataframe(user_df)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=True, resizable=True)

    # 設定 editable 欄位
    gb.configure_column("note", editable=True)
    gb.configure_column("is_admin", editable=True, cellEditor="agCheckboxCellEditor")

    # 根據選取的列動態設定 is_active 為下拉選單
    def is_active_editor(row):
        if row["is_active"] == "啟用中":
            return ["啟用中", "停用帳號", "刪除帳號"]
        else:
            return ["已停用", "啟用帳號", "刪除帳號"]

    # 預設先設定所有選項
    gb.configure_column("is_active", editable=True, cellEditor="agSelectCellEditor",
        cellEditorParams={"values": ["啟用中", "停用帳號", "啟用帳號", "刪除帳號"]})

    grid_options = gb.build()

    grid_return = AgGrid(
        user_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=380,
        theme="streamlit",
        allow_unsafe_jscode=True
    )

    selected_rows = grid_return["selected_rows"]
    edited_df = grid_return["data"]

    if st.button("💾 儲存變更"):
        for row in selected_rows:
            user_id = row['id']
            new_row = edited_df[edited_df['id'] == user_id].iloc[0]
            original_row = next((u for u in users if u['id'] == user_id), None)

            # 狀態變更處理
            status = new_row['is_active']
            if status == "啟用帳號":
                requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
            elif status == "停用帳號":
                requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
            elif status == "刪除帳號":
                requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

            # 其餘欄位更新
            payload = {
                "is_admin": new_row['is_admin'],
                "note": new_row['note'] if pd.notna(new_row['note']) else ""
            }
            requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

        st.success("✅ 帳號更新完成！請重新整理頁面查看最新狀態。")

def run():
    main()
