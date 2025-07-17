import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from frontend.utils.api import get_api_base_url

API_BASE_URL = get_api_base_url()

def get_all_users():
    try:
        response = requests.get(f"{API_BASE_URL}/users")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("❌ 無法取得使用者資料。")
            return []
    except Exception as e:
        st.error(f"❌ 發生錯誤：{e}")
        return []

def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    # 欄位對應：英文 → 中文
    rename_map = {
        "id": "使用者ID",
        "username": "帳號名稱",
        "company": "公司名稱",
        "is_admin": "是否為管理員",
        "is_active": "狀態",
        "note": "備註"
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # 補欄位（若後端沒回傳）
    for col in ["公司名稱", "狀態", "是否為管理員", "備註"]:
        if col not in df.columns:
            df[col] = ""

    # 將 True/False 的狀態轉換為文字
    df["狀態"] = df["狀態"].apply(lambda x: "啟用中" if x else "已停用")

    return df

def update_user(user):
    user_id = user["使用者ID"]
    payload = {
        "is_admin": user["是否為管理員"],
        "note": user["備註"]
    }
    try:
        response = requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)
        return response.status_code == 200
    except:
        return False

def change_user_status(user_id, action):
    try:
        url = f"{API_BASE_URL}/"
        if action == "啟用中":
            url += f"enable_user/{user_id}"
        elif action == "停用帳號":
            url += f"disable_user/{user_id}"
        elif action == "刪除帳號":
            url += f"delete_user/{user_id}"
        response = requests.put(url)
        return response.status_code == 200
    except:
        return False

def run():
    st.markdown("""
        <h2 style='display: flex; align-items: center;'>
            <span style='font-size: 1.8em;'>🧑‍💼 帳號清單</span>
        </h2>
    """, unsafe_allow_html=True)

    users = get_all_users()
    if not users:
        st.warning("⚠️ 尚無有效使用者資料，請稍後再試。")
        return

    df = process_users(users)

    # 檢查欄位是否齊全
    required_cols = ["使用者ID", "帳號名稱", "公司名稱", "是否為管理員", "狀態", "備註"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠️ 回傳資料缺少欄位：{', '.join(missing_cols)}")
        return

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False)

    gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor",
                        cellEditorParams={"values": ["啟用中", "停用帳號", "刪除帳號"]})
    gb.configure_column("備註", editable=True)
    gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")

    gridOptions = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MANUAL,
        height=380,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        theme="streamlit"
    )

    updated_rows = grid_response["data"]
    selected_rows = updated_rows

    if st.button("💾 儲存變更"):
        success = True
        for _, user in selected_rows.iterrows():
            update_success = update_user(user)
            status_success = change_user_status(user["使用者ID"], user["狀態"])
            if not update_success or not status_success:
                success = False
        if success:
            st.success("✅ 所有變更已成功儲存！")
        else:
            st.error("❌ 儲存過程中有部分失敗，請稍後再試。")

    st.markdown("""
        <br>
        <a href="/" target="_self">
            <button style='padding: 0.4em 1.2em; font-size: 1.1em;'>🔙 返回主頁</button>
        </a>
    """, unsafe_allow_html=True)
