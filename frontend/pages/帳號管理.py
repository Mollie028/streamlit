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

# 取得使用者資料
users = get_users()
if not users:
    st.stop()

# 資料前處理：加上中文欄位
for user in users:
    user["使用者ID"] = user.get("id")
    user["帳號名稱"] = user.get("username")
    user["公司名稱"] = user.get("company_name", "")
    user["是否為管理員"] = bool(user.get("is_admin", False))
    user["備註"] = user.get("note", "")
    user["狀態"] = "啟用中" if user.get("is_active") else "停用帳號"

# 建立 DataFrame
df_display = pd.DataFrame(users)[["使用者ID", "帳號名稱", "公司名稱", "是否為管理員", "狀態", "備註"]]

# AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df_display)
gb.configure_selection("multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": ["啟用中", "停用帳號", "啟用帳號", "刪除帳號"]})
gb.configure_column("備註", editable=True)

# 顯示表格
grid_return = AgGrid(
    df_display,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    height=380,
    theme="streamlit",
    allow_unsafe_jscode=True,
    return_mode="AS_INPUT"  # ✅ 關鍵設定，讓 selected_rows 是 dict
)

selected_rows = grid_return["selected_rows"]

# 儲存變更
if st.button("💾 儲存變更"):
    if not selected_rows:
        st.warning("請先選擇至少一筆帳號再儲存變更。")
    else:
        for row in selected_rows:
            user_id = row.get("使用者ID")
            status = row.get("狀態")

            # 呼叫狀態 API
            if status == "啟用帳號":
                requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
            elif status == "停用帳號":
                requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
            elif status == "刪除帳號":
                requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

            # 更新備註與管理員
            payload = {
                "is_admin": row.get("是否為管理員", False),
                "note": row.get("備註", "")
            }
            requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

        st.success("✅ 帳號更新完成！可重新整理查看最新狀態。")

# 返回按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")  # ⚠️ 改成你要返回的頁面（或留空自行處理跳轉邏輯）


# 包成 run() 方便外部呼叫
def run():
    main()
