import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import requests

st.set_page_config(page_title="帳號管理", layout="wide")

st.markdown("""
    <style>
        .main .block-container {padding-top: 2rem;}
        .ag-theme-streamlit {height: 380px;}
        .stButton>button {margin-top: 10px; margin-right: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🔐 帳號管理頁面")

API_URL = "https://ocr-whisper-production-2.up.railway.app"

# ======================== 權限檢查 ========================
if 'user_info' not in st.session_state or not st.session_state['user_info'].get("is_admin"):
    st.warning("⚠️ 僅限管理員使用此頁面")
    st.stop()

# ======================== 搜尋條件區 ========================
st.markdown("### 🔎 搜尋帳號")
col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("輸入帳號名稱或 ID 進行搜尋", "")
with col2:
    if st.button("🔍 搜尋"):
        st.session_state["search_keyword"] = keyword
keyword = st.session_state.get("search_keyword", "")

# ======================== 取得使用者資料 ========================
def get_users():
    try:
        res = requests.get(f"{API_URL}/users")
        if res.status_code == 200:
            return res.json()
        else:
            st.error("無法取得使用者資料")
    except Exception as e:
        st.error(f"發生錯誤：{e}")
    return []

users_data = get_users()

if keyword:
    users_data = [u for u in users_data if keyword.lower() in str(u['id']).lower() or keyword.lower() in u['username'].lower()]

if not users_data:
    st.info("查無資料")
    st.stop()

# ======================== 設定 AgGrid 表格 ========================
for u in users_data:
    u['啟用中'] = '啟用' if u['is_active'] else '停用'
    u['權限'] = '管理員' if u['is_admin'] else '使用者'

gb = GridOptionsBuilder.from_dataframe(
    st.experimental_data_editor(users_data, disabled=True)
)
gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_default_column(editable=True)
gb.configure_column("id", header_name="ID", editable=False, width=70)
gb.configure_column("username", header_name="帳號")
gb.configure_column("is_admin", header_name="is_admin", editable=False, width=100)
gb.configure_column("company", header_name="公司")
gb.configure_column("啟用中", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['啟用', '停用']})
gb.configure_column("權限", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['使用者', '管理員']})
gb.configure_column("note", header_name="備註")
gb.configure_column("操作", editable=False, valueGetter="'停用帳號'")

grid_response = AgGrid(
    users_data,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MANUAL,
    fit_columns_on_grid_load=True,
    height=380,
    theme='streamlit'
)

updated_rows = grid_response["data"]

# ======================== 儲存變更 ========================
st.markdown("### 💾 儲存帳號變更")
if st.button("✅ 儲存變更"):
    success_count = 0
    fail_list = []
    for row in updated_rows:
        try:
            user_id = row["id"]
            if row['username'] == "admin" or row['is_admin']:
                continue  # 不允許改管理員資料

            updated_payload = {
                "company": row.get("company", ""),
                "note": row.get("note", ""),
                "is_active": row["啟用中"] == "啟用",
                "is_admin": row["權限"] == "管理員"
            }
            res = requests.put(f"{API_URL}/update_user/{user_id}", json=updated_payload)
            if res.status_code == 200:
                success_count += 1
            else:
                fail_list.append(user_id)
        except:
            fail_list.append(row['id'])

    if success_count:
        st.success(f"成功更新 {success_count} 筆帳號")
    if fail_list:
        st.error(f"以下帳號更新失敗：{fail_list}")

# ======================== 密碼修改區 ========================
st.markdown("### 🔐 修改密碼")
selected_user = st.selectbox("請選擇要修改密碼的帳號：", [u['username'] for u in users_data if not u['is_admin']])
new_password = st.text_input("輸入新密碼", type="password")
if st.button("🔐 送出密碼修改"):
    selected_user_id = next((u['id'] for u in users_data if u['username'] == selected_user), None)
    if selected_user_id:
        res = requests.put(f"{API_URL}/update_user_password/{selected_user_id}", json={"new_password": new_password})
        if res.status_code == 200:
            st.success(f"✅ {selected_user} 密碼修改成功")
        else:
            st.error("密碼修改失敗")

# ======================== 返回主頁 ========================
if st.button("⬅️ 返回主頁"):
    st.switch_page("app.py")
