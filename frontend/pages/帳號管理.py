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

def main():
    users = get_users()
    if not users:
        st.stop()

    for user in users:
        user["是否為管理員"] = bool(user["is_admin"])
        user["帳號名稱"] = user["username"]
        user["公司名稱"] = user["company_name"]
        user["備註"] = user["note"]
        user["狀態"] = "啟用中" if user["is_active"] else "停用帳號"

    df_display = pd.DataFrame(users)[["id", "帳號名稱", "公司名稱", "是否為管理員", "狀態", "備註"]]
    df_display = df_display.rename(columns={"id": "使用者ID"})

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

    # 返回按鈕
    if st.button("🔙 返回首頁"):
        st.switch_page("/app.py")

    # 儲存變更按鈕
    if st.button("💾 儲存變更"):
        if selected_rows is None or len(selected_rows) == 0:
            st.warning("請先勾選至少一筆使用者資料。")
            return

        for row in selected_rows:
            user_id = row.get("使用者ID")
            if not user_id:
                continue
            status = row.get("狀態", "")

            # 呼叫狀態 API
            if status == "啟用帳號":
                requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
            elif status == "停用帳號":
                requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
            elif status == "刪除帳號":
                requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

            # 其他欄位更新
            payload = {
                "is_admin": row.get("是否為管理員", False),
                "note": row.get("備註", "") or ""
            }
            requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

        st.success("✅ 帳號更新完成！請重新整理頁面查看最新狀態。")

def run():
    main()
