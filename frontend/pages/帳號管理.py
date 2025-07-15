import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

API_BASE = st.secrets["API_BASE"]

st.set_page_config(page_title="帳號管理", layout="wide")
st.markdown("## 🧑‍💼 帳號管理區")

# 取得帳號資料
def get_users():
    try:
        res = requests.get(f"{API_BASE}/users")
        res.raise_for_status()
        users = res.json()
        for user in users:
            user["啟用中"] = user.get("enabled", True)
        return users
    except Exception as e:
        st.error(f"無法取得帳號資料：{e}")
        return []

# 顯示搜尋框
search_term = st.text_input("🔍 搜尋帳號／公司／備註")

# 取得資料
users_data = get_users()
if search_term:
    users_data = [u for u in users_data if search_term.lower() in str(u).lower()]

# 資料轉為 DataFrame
if users_data:
    df = pd.DataFrame(users_data)
    df.rename(columns={
        "id": "ID",
        "username": "帳號",
        "is_admin": "管理員",
        "company": "公司",
        "啟用中": "啟用中",
        "note": "備註"
    }, inplace=True)

    # 建立 Grid
    gb = GridOptionsBuilder.from_dataframe(df[["ID", "帳號", "管理員", "公司", "啟用中", "備註"]])
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=True)
    gb.configure_column("ID", editable=False)
    gb.configure_column("帳號", editable=False)
    gb.configure_selection("multiple", use_checkbox=True)
    gridOptions = gb.build()

    st.markdown("### 📋 帳號清單")
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        theme="balham"
    )

    selected_rows = grid_response["selected_rows"]
    edited_df = grid_response["data"]

    # 儲存變更按鈕與功能
    if st.button("💾 儲存變更"):
        for index, row in edited_df.iterrows():
            user_id = row["ID"]
            payload = {
                "is_admin": row["管理員"],
                "enabled": row["啟用中"],
                "note": row["備註"]
            }
            try:
                res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload)
                res.raise_for_status()
            except Exception as e:
                st.error(f"更新 ID {user_id} 失敗：{e}")
        st.success("✅ 所有變更已儲存！")

    # 顯示修改密碼欄位
    if selected_rows:
        if len(selected_rows) == 1:
            st.markdown("---")
            st.markdown("### 🔐 修改密碼")
            new_pw = st.text_input("請輸入新密碼", type="password")
            if st.button("🛠 修改密碼"):
                user_id = selected_rows[0]["ID"]
                try:
                    res = requests.put(f"{API_BASE}/update_user_password/{user_id}", json={"password": new_pw})
                    res.raise_for_status()
                    st.success("密碼修改成功！")
                except Exception as e:
                    st.error(f"密碼修改失敗：{e}")

else:
    st.warning("⚠️ 無帳號資料可顯示")
