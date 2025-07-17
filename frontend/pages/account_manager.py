import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import requests
from frontend.utils.api import get_api_base_url

API_BASE_URL = get_api_base_url()

def fetch_users():
    try:
        response = requests.get(f"{API_BASE_URL}/users")
        response.raise_for_status()
        users = response.json()
        return users
    except Exception as e:
        st.error(f"無法取得使用者資料：{e}")
        return []

def process_users(users):
    if not users:
        return pd.DataFrame()

    df = pd.DataFrame(users)

    # 中文欄位命名
    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "is_admin": "是否為管理員",
        "company": "所屬公司",
        "is_active": "啟用中",
        "note": "備註",
        "status": "狀態"
    })

    # 狀態選項下拉選單
    def status_dropdown(status):
        if status == "啟用中":
            return ["啟用中", "停用帳號", "刪除帳號"]
        else:
            return ["停用中", "啟用帳號", "刪除帳號"]

    df["狀態"] = df["啟用中"].apply(lambda x: "啟用中" if x else "停用中")
    df["狀態選單"] = df["狀態"].apply(status_dropdown)

    return df

def update_users(updated_df):
    for _, row in updated_df.iterrows():
        user_id = row["使用者ID"]
        status = row["狀態"]
        note = row.get("備註", "")

        if status == "啟用帳號":
            requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
        elif status == "停用帳號":
            requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
        elif status == "刪除帳號":
            requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

        # 更新備註
        requests.put(f"{API_BASE_URL}/update_user/{user_id}", json={"note": note})

def run():
    st.title("👩🏻‍💼 帳號清單")

    users = fetch_users()
    df = process_users(users)

    if df.empty:
        st.warning("⚠ 尚無有效使用者資料，請稍後再試。")
        return

    # 顯示欄位
    display_df = df[["使用者ID", "帳號名稱", "是否為管理員", "所屬公司", "啟用中", "備註", "狀態", "狀態選單"]]

    # 建立 AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_column("備註", editable=True)
    gb.configure_column("狀態", editable=True, cellEditor='agSelectCellEditor',
                        cellEditorParams={"values": ["啟用中", "停用帳號", "啟用帳號", "刪除帳號"]})
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=380
    )

    selected_rows = grid_response["data"]

    # 儲存變更按鈕
    if st.button("💾 儲存變更"):
        if selected_rows is not None:
            update_users(pd.DataFrame(selected_rows))
            st.success("✅ 已成功儲存變更！")
            st.experimental_rerun()
        else:
            st.warning("請至少選取一筆資料進行變更。")

    if st.button("🔙 返回主頁"):
        st.switch_page("app.py")
