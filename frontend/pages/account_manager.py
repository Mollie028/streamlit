import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from core.config import API_BASE
from services.auth_service import is_logged_in, logout_button

st.set_page_config(page_title="帳號管理", layout="wide")

# ✅ 登入檢查
if not is_logged_in():
    st.warning("請先登入以使用本功能")
    st.stop()

# ✅ 登出按鈕
logout_button()

# ✅ 判斷使用者角色
is_admin = st.session_state.get("role", "") == "admin"

# ✅ 顯示標題與提示
st.title("帳號管理")
st.markdown("以下為所有使用者帳號資料，僅限管理員修改")

# ✅ 載入使用者資料
res = requests.get(f"{API_BASE}/users")
users = res.json() if res.status_code == 200 else []
df = pd.DataFrame(users)

if df.empty:
    st.warning("尚無使用者資料")
    st.stop()

# ✅ 顯示欄位與順序
df = df[["id", "username", "is_admin", "is_active", "note"]]
df.rename(columns={
    "id": "ID",
    "username": "使用者帳號",
    "is_admin": "是否為管理員",
    "is_active": "使用者狀況",
    "note": "備註"
}, inplace=True)

# ✅ 將布林值轉換成「啟用／停用」
df["使用者狀況"] = df["使用者狀況"].apply(lambda x: "啟用" if x else "停用")

# ✅ 建立 AgGrid 表格選項
builder = GridOptionsBuilder.from_dataframe(df)
builder.configure_default_column(editable=False)

builder.configure_column("ID", pinned="left", editable=False)
builder.configure_column("使用者帳號", pinned="left", editable=False)
builder.configure_column("是否為管理員", editable=is_admin, cellEditor="agSelectCellEditor",
                         cellEditorParams={"values": [True, False]})
builder.configure_column("使用者狀況", editable=is_admin, cellEditor="agSelectCellEditor",
                         cellEditorParams={"values": ["啟用", "停用", "刪除"]})
builder.configure_column("備註", editable=is_admin)

grid_options = builder.build()

st.markdown("### 👥 使用者帳號清單")
grid_return = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MANUAL,
    theme="blue",
    fit_columns_on_grid_load=True,
    height=380
)

updated_df = grid_return["data"]

# ✅ 儲存按鈕
if st.button("💾 儲存變更"):
    for i, row in updated_df.iterrows():
        user_id = row["ID"]

        # 狀態處理
        status = row["使用者狀況"]
        if status == "啟用":
            requests.put(f"{API_BASE}/enable_user/{user_id}")
        elif status == "停用":
            requests.put(f"{API_BASE}/disable_user/{user_id}")
        elif status == "刪除":
            requests.delete(f"{API_BASE}/delete_user/{user_id}")

        # 權限與備註更新
        if is_admin:
            payload = {
                "is_admin": row["是否為管理員"],
                "note": row["備註"]
            }
            requests.put(f"{API_BASE}/update_user/{user_id}", json=payload)

    st.success("✅ 帳號更新完成，請重新整理頁面查看最新狀態")
