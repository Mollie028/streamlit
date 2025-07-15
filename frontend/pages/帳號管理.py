import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

# 讓用戶發現 secrets 未設定時的錯誤
try:
    "API_BASE = "https://ocr-whisper-production-2.up.railway.app"
    
except KeyError:
    st.error("🚨 請至 Settings → Secrets 設定 API_BASE")
    st.stop()

st.title("\U0001f5c3️ 帳號管理")

# ---- 請求 API 取得帳號列表 ---- #
@st.cache_data(show_spinner=False)
def get_users():
    res = requests.get(f"{API_BASE}/users")
    if res.status_code == 200:
        return res.json()
    else:
        st.error("無法取得帳號資料")
        return []

users = get_users()
df = pd.DataFrame(users)

# 預設格式處理
if 'enabled' in df.columns:
    df["啟用中"] = df["enabled"]
if 'role' in df.columns:
    df["管理員"] = df["role"].apply(lambda x: x == 'admin')
if 'note' not in df.columns:
    df["note"] = ""

# ---- AgGrid 主表格 ---- #
st.markdown("### 帳號清單")

gb = GridOptionsBuilder.from_dataframe(df[["id", "username", "管理員", "company", "啟用中", "note"]])
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_column("id", header_name="ID", editable=False)
gb.configure_column("username", header_name="帳號", editable=False)
gb.configure_column("管理員", header_name="管理員", editable=True)
gb.configure_column("company", header_name="公司", editable=False)
gb.configure_column("啟用中", header_name="啟用中", editable=True)
gb.configure_column("note", header_name="備註", editable=True)

# 列選標記 + 允許編輯
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=300
)

selected_rows = grid_response["selected_rows"]
updated_df = grid_response["data"]

# ---- 啟用 / 停用 / 刪除功能展示與啟用 ---- #
st.markdown("### 設定帳號狀態")
if selected_rows:
    ids = [r["id"] for r in selected_rows]
    for id_ in ids:
        row = updated_df[updated_df["id"] == id_].iloc[0]
        payload = {
            "enabled": row["啟用中"],
            "role": "admin" if row["管理員"] else "user",
            "note": row["note"]
        }
        res = requests.put(f"{API_BASE}/update_user/{id_}", json=payload)
        if res.status_code == 200:
            st.success(f"ID {id_} 資料更新成功")
        else:
            st.error(f"ID {id_} 更新失敗")
else:
    st.info("\U0001f50d 請選擇想編輯的帳號")

# ---- 修改密碼 ---- #
st.markdown("### 修改密碼")
if selected_rows and len(selected_rows) == 1:
    user_id = selected_rows[0]["id"]
    new_pw = st.text_input("請輸入新密碼", type="password")
    if st.button("修改密碼"):
        if new_pw:
            res = requests.put(f"{API_BASE}/update_user_password/{user_id}", json={"new_password": new_pw})
            if res.status_code == 200:
                st.success("密碼修改成功")
            else:
                st.error("API 失敗")
        else:
            st.warning("請輸入新密碼")
else:
    st.info("\U0001f512 請選擇一個帳號進行密碼修改")
