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

st.markdown("## 👤 帳號清單")

@st.cache_data
def get_users():
    try:
        res = requests.get(f"{API_BASE_URL}/users")
        if res.status_code == 200:
            return res.json()
        else:
            st.error("❌ 無法取得使用者資料。")
            return []
    except Exception as e:
        st.error("❌ 連線錯誤：" + str(e))
        return []

# 取得資料
users = get_users()
if not users:
    st.stop()

# 前處理
for user in users:
    user["是否為管理員"] = bool(user["is_admin"])
    user["帳號名稱"] = user["username"]
    user["公司名稱"] = user["company_name"]
    user["備註"] = user["note"]
    user["狀態"] = "啟用中" if user["is_active"] else "停用帳號"
    user["使用者ID"] = user["id"]

# 轉成表格
df_display = pd.DataFrame(users)[["使用者ID", "帳號名稱", "公司名稱", "是否為管理員", "狀態", "備註"]]

# AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df_display)
gb.configure_selection("multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": ["啟用中", "停用帳號", "啟用帳號", "刪除帳號"]})
gb.configure_column("備註", editable=True)

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

# 儲存變更按鈕
if st.button("💾 儲存變更"):
    for row in selected_rows:
        user_id = row["使用者ID"]
        status = row["狀態"]

        # 呼叫狀態 API
        if status == "啟用帳號":
            requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
        elif status == "停用帳號":
            requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
        elif status == "刪除帳號":
            requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

        # 其他欄位更新
        payload = {
            "is_admin": row["是否為管理員"],
            "note": row["備註"] if pd.notna(row["備註"]) else ""
        }
        requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

    st.success("✅ 帳號更新完成！請重新整理頁面查看最新狀態。")


def run():
    main()
