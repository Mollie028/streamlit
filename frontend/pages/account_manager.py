import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from utils.auth import is_logged_in, logout_button
from core.config import API_BASE

st.set_page_config(page_title="帳號管理", layout="wide")
st.title("🧑‍💼 帳號管理")

if not is_logged_in():
    st.warning("請先登入後再操作。")
    st.stop()

# ✅ 加上返回主頁按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")

# ✅ 取得目前使用者登入角色
current_user = st.session_state.get("username")
is_admin = st.session_state.get("role") == "admin"

# ✅ 欄位中文對照表
column_mapping = {
    "id": "ID",
    "username": "使用者帳號",
    "is_admin": "是否為管理員",
    "is_active": "使用者狀況",
    "note": "備註"
}

# ✅ 下拉選單選項
status_options = ["啟用", "停用", "刪除"]

# ✅ 呼叫 API 取得帳號清單
def fetch_users():
    try:
        res = requests.get(f"{API_BASE}/users")
        if res.status_code == 200:
            return res.json()
        else:
            st.error("無法取得帳號資料。")
            return []
    except Exception as e:
        st.error(f"API 錯誤：{str(e)}")
        return []

# ✅ 將 is_active 欄位轉為中文顯示
def map_status(value):
    if value == True:
        return "啟用"
    elif value == False:
        return "停用"
    return "刪除"

def reverse_status(value):
    return True if value == "啟用" else False if value == "停用" else None

# ✅ 載入並預處理帳號資料
users = fetch_users()
df = pd.DataFrame(users)
if not df.empty:
    df = df[["id", "username", "is_admin", "is_active", "note"]]
    df["is_active"] = df["is_active"].apply(map_status)
    df.rename(columns=column_mapping, inplace=True)

    # ✅ AgGrid 設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False, resizable=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("是否為管理員", editable=is_admin, cellEditor="agSelectCellEditor", cellEditorParams={"values": [True, False]})
    gb.configure_column("使用者狀況", editable=is_admin, cellEditor="agSelectCellEditor", cellEditorParams={"values": status_options})

    gb.configure_grid_options(domLayout='normal')
    gb.configure_grid_options(suppressMovableColumns=True)  # ✅ 禁止欄位拖曳
    grid_options = gb.build()

    st.markdown("#### 👇 編輯帳號資訊後，按下下方【儲存變更】")
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=True,
        height=380,
        allow_unsafe_jscode=True,
        theme="streamlit"
    )

    updated_df = grid_response["data"]

    # ✅ 儲存按鈕
    if st.button("💾 儲存變更"):
        for i, row in updated_df.iterrows():
            uid = row["ID"]
            status = reverse_status(row["使用者狀況"])
            payload = {
                "note": row["備註"],
                "is_admin": row["是否為管理員"] if is_admin else None,
                "is_active": status if is_admin else None
            }
            # 避免非管理員亂改他人資料
            if not is_admin and row["使用者帳號"] != current_user:
                continue
            try:
                res = requests.put(f"{API_BASE}/update_user/{uid}", json=payload)
                if res.status_code == 200:
                    continue
                else:
                    st.error(f"更新失敗：{res.text}")
            except Exception as e:
                st.error(f"更新錯誤：{e}")

        st.success("✅ 變更已儲存！請重新整理或登出再登入查看結果。")

else:
    st.info("尚無使用者資料。")

# ✅ 登出鈕
logout_button()
