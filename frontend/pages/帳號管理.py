import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import pandas as pd

# 取得 API_BASE
try:
    API_BASE = st.secrets["API_BASE"]
except KeyError:
    st.error("🚨 請至 Settings → Secrets 設定 API_BASE")
    st.stop()

st.title("🧑‍💼 帳號管理面板")

# 取得帳號資料
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

# 格式處理
if 'enabled' in df.columns:
    df["啟用中"] = df["enabled"]
if 'role' in df.columns:
    df["管理員"] = df["role"].apply(lambda x: x == 'admin')
if 'note' not in df.columns:
    df["note"] = ""
df["動作"] = "無操作"

# AgGrid 表格設定
gb = GridOptionsBuilder.from_dataframe(df[["id", "username", "管理員", "公司", "啟用中", "note", "動作"]])
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_column("id", header_name="ID", editable=False, width=70)
gb.configure_column("username", header_name="帳號", editable=False, width=120)
gb.configure_column("管理員", header_name="管理員", editable=True, width=90)
gb.configure_column("公司", header_name="公司", editable=False, width=120)
gb.configure_column("啟用中", header_name="啟用中", editable=True, width=90)
gb.configure_column("note", header_name="備註", editable=True, width=160)
gb.configure_column("動作", header_name="動作", editable=True, width=120,
    cellEditor='agSelectCellEditor',
    cellEditorParams={"values": ["無操作", "停用帳號", "刪除帳號"]})

gb.configure_selection(selection_mode="multiple", use_checkbox=True)
grid_options = gb.build()

# 顯示 AgGrid
with st.container():
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        height=300
    )

updated_df = grid_response["data"]
selected_rows = grid_response["selected_rows"]

# 儲存變更區塊
st.markdown("### 🛠️ 帳號操作")
if st.button("💾 儲存變更"):
    for index, row in updated_df.iterrows():
        user_id = row["id"]
        action = row["動作"]

        # 處理更新欄位
        payload = {
            "enabled": row["啟用中"],
            "role": "admin" if row["管理員"] else "user",
            "note": row["note"]
        }
        res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload)
        if res.status_code == 200:
            st.success(f"✅ ID {user_id} 資料更新成功")
        else:
            st.error(f"❌ ID {user_id} 更新失敗")

        # 處理帳號動作
        if action == "停用帳號":
            res2 = requests.put(f"{API_BASE}/update_user/{user_id}", json={"enabled": False})
            if res2.status_code == 200:
                st.success(f"🔒 ID {user_id} 已停用")
            else:
                st.error(f"❌ ID {user_id} 停用失敗")

        elif action == "刪除帳號":
            res3 = requests.delete(f"{API_BASE}/delete_user/{user_id}")
            if res3.status_code == 200:
                st.success(f"🗑️ ID {user_id} 已刪除")
            else:
                st.error(f"❌ ID {user_id} 刪除失敗")

# 修改密碼區塊
st.markdown("### 🔐 修改密碼")
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
    st.info("🔒 請選擇一個帳號進行密碼修改")
