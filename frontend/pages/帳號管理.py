import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from streamlit_extras.stylable_container import stylable_container

API_BASE = "https://ocr-whisper-production-2.up.railway.app"

# -------- 取得帳號清單 -------- #
@st.cache_data

def get_users():
    res = requests.get(f"{API_BASE}/users")
    if res.status_code == 200:
        return res.json()
    else:
        st.error("無法取得帳號資料")
        return []

# -------- 更新帳號狀態 -------- #
def update_user_status(user_id, enabled):
    requests.put(f"{API_BASE}/update_user_status/{user_id}", json={"enabled": enabled})

# -------- 更新帳號角色 -------- #
def update_user_role(user_id, role):
    requests.put(f"{API_BASE}/update_user_role/{user_id}", json={"role": role})

# -------- 更新帳號備註 -------- #
def update_user_note(user_id, note):
    requests.put(f"{API_BASE}/update_user_note/{user_id}", json={"note": note})

# -------- 顯示修改密碼欄 -------- #
def modify_password(user_id):
    with stylable_container(key="pwd", css="border: 1px solid #ccc; padding: 1rem; margin-top: 2rem;"):
        st.subheader("🔐 修改密碼")
        new_password = st.text_input("請輸入新密碼", type="password")
        if st.button("🛠️ 修改密碼"):
            if new_password:
                res = requests.put(f"{API_BASE}/update_user_password/{user_id}", json={"new_password": new_password})
                if res.status_code == 200:
                    st.success("密碼修改成功！")
                else:
                    st.error("密碼修改失敗")
            else:
                st.warning("請輸入新密碼")

# -------- AgGrid 表格 -------- #
st.markdown("## 🧑‍💼 帳號管理系統")
st.markdown("🔍 搜尋帳號 / 公司 / 備註")

users = get_users()

for user in users:
    user["啟用中"] = user["enabled"]
    user["管理員"] = user["role"] == "admin"

gb = GridOptionsBuilder.from_dataframe(
    pd.DataFrame(users)[["id", "username", "管理員", "company", "啟用中", "note"]]
)
gb.configure_default_column(editable=True, resizable=True)
gb.configure_column("id", width=70)
gb.configure_column("username", header_name="帳號", width=150)
gb.configure_column("管理員", cellEditor="agCheckboxCellEditor", width=100)
gb.configure_column("啟用中", cellEditor="agCheckboxCellEditor", width=100)
gb.configure_column("note", header_name="備註", width=250)
gb.configure_selection("multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)

response = AgGrid(
    pd.DataFrame(users),
    gridOptions=gb.build(),
    height=400,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    theme="alpine"
)

selected_rows = response["selected_rows"]
edited_rows = response["data"]

# -------- 儲存變更 -------- #
st.markdown("---")
if st.button("💾 儲存變更"):
    for edited in edited_rows:
        user_id = edited["id"]
        update_user_status(user_id, edited["啟用中"])
        update_user_role(user_id, "admin" if edited["管理員"] else "user")
        update_user_note(user_id, edited.get("note", ""))
    st.success("✅ 所有變更已儲存")

# -------- 密碼修改區塊 -------- #
if selected_rows:
    selected_user = selected_rows[0]
    modify_password(selected_user["id"])
