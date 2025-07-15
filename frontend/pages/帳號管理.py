import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import pandas as pd

API_BASE = "https://你的後端網址"
st.set_page_config(page_title="帳號管理", layout="wide")

st.title("🧑‍💼 帳號管理")

# 搜尋欄
search = st.text_input("🔍 搜尋帳號、公司或備註", key="search_input")

# 取得使用者列表
@st.cache_data
def get_users():
    res = requests.get(f"{API_BASE}/users")
    return res.json() if res.status_code == 200 else []

data = get_users()
df = pd.DataFrame(data)

# 篩選
if search:
    df = df[df.apply(lambda row: search.lower() in str(row["username"]).lower()
                     or search.lower() in str(row["company"] or "").lower()
                     or search.lower() in str(row["note"] or "").lower(), axis=1)]

# 定義可編輯欄位
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination()
gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
gb.configure_grid_options(domLayout="normal")
gb.configure_column("admin", editable=True, cellEditor="agCheckboxCellEditor", header_name="管理員")
gb.configure_column("active", editable=True, cellEditor="agCheckboxCellEditor", header_name="啟用中")
gb.configure_column("note", editable=True, header_name="備註")
gb.configure_column("company", editable=False, header_name="公司")
gb.configure_column("username", editable=False, header_name="帳號")
gb.configure_column("id", editable=False, header_name="ID")

# 新增操作欄：停用與刪除按鈕
button_code = JsCode("""
function(params) {
    return `
    <button onclick="window.dispatchEvent(new CustomEvent('停用', {detail: ${params.data.id}}))">🛑</button>
    <button onclick="window.dispatchEvent(new CustomEvent('刪除', {detail: ${params.data.id}}))">🗑️</button>
    `;
}
""")
gb.configure_column("操作", header_name="操作", cellRenderer=button_code, editable=False)

# 填滿畫面
grid_height = max(500, len(df)*50)
grid_options = gb.build()
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    fit_columns_on_grid_load=True,
    update_mode=GridUpdateMode.MANUAL,
    allow_unsafe_jscode=True,
    height=grid_height,
    reload_data=True,
)

updated_rows = grid_response["data"]

# 儲存變更
if st.button("💾 儲存變更"):
    for index, row in updated_rows.iterrows():
        user_id = row["id"]
        payload = {
            "note": row.get("note", ""),
            "admin": row.get("admin", False),
            "active": row.get("active", False),
        }
        res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload)
        if res.status_code == 200:
            st.success(f"✅ 使用者 {row['username']} 更新成功")
        else:
            st.error(f"❌ 使用者 {row['username']} 更新失敗")
    st.cache_data.clear()

# 處理表格內按鈕事件（Streamlit 不支援 JS callback，僅限前端示意）
st.warning("⚠️ 注意：表格內的 🛑 / 🗑️ 按鈕僅為示意，如需後端處理，需用 Streamlit events 實作或改為外部按鈕")
