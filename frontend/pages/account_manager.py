import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sys
import os

# ✅ 加入路徑以正確匯入模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from core.config import API_BASE
from utils.auth import is_logged_in, logout_button

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
try:
    res = requests.get(f"{API_BASE}/users")
    users = res.json()
except Exception as e:
    st.error(f"讀取帳號列表失敗：{e}")
    st.stop()

# ✅ 整理資料為 DataFrame
df = pd.DataFrame(users)
if df.empty:
    st.info("目前沒有使用者資料")
    st.stop()

# ✅ 欄位重新命名與排序
df = df.rename(columns={
    "id": "ID",
    "username": "使用者帳號",
    "is_admin": "是否為管理員",
    "is_active": "使用者狀況",
    "note": "備註"
})[["ID", "使用者帳號", "是否為管理員", "使用者狀況", "備註"]]

# ✅ 將使用者狀況轉換為中文
status_map = {True: "啟用", False: "停用", "deleted": "刪除"}
reverse_status_map = {"啟用": True, "停用": False, "刪除": "deleted"}
df["使用者狀況"] = df["使用者狀況"].map(status_map)

# ✅ 建立欄位設定
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, resizable=False)
gb.configure_column("是否為管理員", editable=is_admin)
gb.configure_column("備註", editable=is_admin)
gb.configure_column("使用者狀況", editable=is_admin, cellEditor="agSelectCellEditor",
                   cellEditorParams={"values": ["啟用", "停用", "刪除"]})
grid_options = gb.build()

# ✅ 表格顯示
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MANUAL,
    height=380,
    allow_unsafe_jscode=True,
    theme="streamlit",
    fit_columns_on_grid_load=True,
    reload_data=True,
    use_checkbox=True,
    enable_enterprise_modules=False
)

# ✅ 儲存變更按鈕
if st.button("💾 儲存變更") and is_admin:
    updated_rows = grid_response["data"]

    for i, row in updated_rows.iterrows():
        user_id = row["ID"]
        update_payload = {
            "note": row["備註"],
            "is_admin": row["是否為管理員"],
            "is_active": reverse_status_map.get(row["使用者狀況"], True)
        }

        status = row["使用者狀況"]
        try:
            if status == "刪除":
                res = requests.delete(f"{API_BASE}/delete_user/{user_id}")
            elif status == "啟用":
                res = requests.put(f"{API_BASE}/enable_user/{user_id}")
                res2 = requests.put(f"{API_BASE}/update_user/{user_id}", json=update_payload)
            elif status == "停用":
                res = requests.put(f"{API_BASE}/disable_user/{user_id}")
                res2 = requests.put(f"{API_BASE}/update_user/{user_id}", json=update_payload)
            else:
                res = requests.put(f"{API_BASE}/update_user/{user_id}", json=update_payload)

        except Exception as e:
            st.error(f"更新 ID {user_id} 時發生錯誤：{e}")
    st.success("✅ 變更已儲存，重新整理頁面以查看最新狀態")

# 🔙 返回主頁
if st.button("← 返回首頁"):
    st.switch_page("app.py")
