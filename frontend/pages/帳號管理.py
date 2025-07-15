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

# 標題與匯出按鈕
col1, col2 = st.columns([1, 5])
with col1:
    st.download_button("⬇️ 匯出帳號清單 (CSV)", data="", file_name="users.csv", disabled=True)
with col2:
    st.markdown("## 🐵 帳號清單")

# 取得使用者資料
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

users = get_users()

if not users:
    st.stop()

# 欄位轉換與下拉選單預設值
for user in users:
    user['is_admin'] = bool(user['is_admin'])
    user['is_active'] = bool(user['is_active'])
    user['action'] = "無操作"

# 表格設定
user_df = pd.DataFrame(users)
gb = GridOptionsBuilder.from_dataframe(user_df)
gb.configure_selection("multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_default_column(editable=True, resizable=True)

# 下拉選單邏輯
for idx, row in user_df.iterrows():
    if row['is_active']:
        user_df.at[idx, 'action'] = "無操作"
    else:
        user_df.at[idx, 'action'] = "無操作"

def get_action_options(row):
    if row['is_active']:
        return ["無操作", "停用帳號", "刪除帳號"]
    else:
        return ["無操作", "啟用帳號", "刪除帳號"]

gb.configure_column("action", editable=True, cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": ["無操作", "停用帳號", "啟用帳號", "刪除帳號"]})

# 顯示表格
grid_options = gb.build()
grid_return = AgGrid(
    user_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    height=380,
    theme="streamlit",
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False
)

selected_rows = grid_return["selected_rows"]
edited_df = grid_return["data"]

# 儲存變更
if st.button("💾 儲存變更"):
    for row in selected_rows:
        user_id = row['id']
        new_row = edited_df[edited_df['id'] == user_id].iloc[0]

        # 檢查帳號狀態變更
        original_user = next((u for u in users if u['id'] == user_id), None)
        if not original_user:
            continue

        # 更新 is_active 狀態
        if new_row['action'] == "停用帳號":
            requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
        elif new_row['action'] == "啟用帳號":
            requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
        elif new_row['action'] == "刪除帳號":
            requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

        # 更新備註欄位與權限設定
        payload = {
            "is_admin": new_row['is_admin'],
            "note": new_row['note'] if pd.notna(new_row['note']) else ""
        }
        requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

    st.success("✅ 帳號更新完成！請重新整理頁面查看最新狀態。")
