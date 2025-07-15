import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

API_BASE_URL = "https://ocr-whisper-production-2.up.railway.app"

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

col1, col2 = st.columns([1, 5])
with col1:
    st.download_button("⬇️ 匯出帳號清單 (CSV)", data="", file_name="users.csv", disabled=True)
with col2:
    st.markdown("## 帳號清單")

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

    # 原始欄位名保留用於送出資料
    for user in users:
        user['is_admin'] = bool(user['is_admin'])
        user['is_active'] = "啟用中" if user['is_active'] else "停用帳號"

    df = pd.DataFrame(users)

    rename_columns = {
        "id": "使用者 ID",
        "username": "帳號名稱",
        "is_admin": "是否為管理員",
        "company_name": "公司名稱",
        "is_active": "狀態",
        "note": "備註"
    }

    df_display = df.rename(columns=rename_columns)

    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=True, resizable=True)

    gb.configure_column("備註", editable=True)
    gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
    gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor",
                        cellEditorParams={"values": ["啟用中", "停用帳號", "啟用帳號", "刪除帳號"]})

    grid_return = AgGrid(
        df_display,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=380,
        theme="streamlit",
        allow_unsafe_jscode=True
    )

    selected_rows = grid_return["selected_rows"]
    edited_df = grid_return["data"]

    # ✅ 儲存變更按鈕補上來
    if st.button("💾 儲存變更"):
        if not selected_rows:
            st.warning("請先選取至少一筆帳號進行變更。")
            st.stop()

        for row in selected_rows:
            try:
                user_id = row["使用者 ID"]
                new_row = edited_df[edited_df["使用者 ID"] == user_id]
                if new_row.empty:
                    st.warning(f"⚠️ 找不到 ID 為 {user_id} 的帳號，略過。")
                    continue

                new_row = new_row.iloc[0]
                status = new_row["狀態"]

                # 狀態處理
                if status == "啟用帳號":
                    requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
                elif status == "停用帳號":
                    requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
                elif status == "刪除帳號":
                    requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

                # 權限與備註更新
                payload = {
                    "is_admin": new_row["是否為管理員"],
                    "note": new_row["備註"] if pd.notna(new_row["備註"]) else ""
                }
                requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)
            except Exception as e:
                st.error(f"❌ 無法更新帳號 ID {row.get('使用者 ID', '?')}：{str(e)}")

        st.success("✅ 帳號更新完成！請重新整理頁面查看最新狀態。")

def run():
    main()
