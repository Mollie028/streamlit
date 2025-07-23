import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils.auth import is_logged_in, logout_button

API_BASE_URL = "https://ocr-whisper-production-2.up.railway.app"

# 登入檢查
user_info = is_logged_in()
if not user_info:
    st.stop()

st.markdown("""
    <h1 style='font-size: 36px;'>🧑‍🤝‍🧑 帳號管理</h1>
    <h2 style='font-size: 24px;'>使用者帳號列表</h2>
""", unsafe_allow_html=True)

# 取得所有使用者資料
def fetch_users():
    try:
        response = requests.get(f"{API_BASE_URL}/users")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("無法取得使用者資料。")
            return []
    except Exception as e:
        st.error(f"請求錯誤：{e}")
        return []

# 更新單一使用者資料
def update_user(user_id, data):
    try:
        response = requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"更新錯誤：{e}")
        return False

users_data = fetch_users()

# 資料預處理
display_data = []
for u in users_data:
    display_data.append({
        "ID": u["id"],
        "使用者帳號": u["username"],
        "是否為管理員": u["is_admin"],
        "使用者狀況": "啟用" if u["is_active"] else "停用",
        "備註": u["note"] or ""
    })

# AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(display_data))
gb.configure_default_column(editable=True)
gb.configure_column("ID", editable=False, pinned="left")
gb.configure_column("使用者帳號", editable=False, pinned="left")
gb.configure_column("是否為管理員", cellEditor="agCheckboxCellEditor")
gb.configure_column("使用者狀況", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用", "停用"]})
gb.configure_column("備註", editable=True)
grid_options = gb.build()

# 顯示 AgGrid 表格
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
response = AgGrid(
    pd.DataFrame(display_data),
    gridOptions=grid_options,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    fit_columns_on_grid_load=True,
    height=380,
    theme="balham",
    allow_unsafe_jscode=True
)

edited_rows = response["data"]

if st.button("💾 儲存變更"):
    update_count = 0
    for index, row in edited_rows.iterrows():
        original = next((u for u in users_data if u["id"] == row["ID"]), None)
        if not original:
            continue

        update_data = {}
        if row["是否為管理員"] != original["is_admin"]:
            update_data["is_admin"] = row["是否為管理員"]
        if row["使用者狀況"] != ("啟用" if original["is_active"] else "停用"):
            update_data["is_active"] = row["使用者狀況"] == "啟用"
        if row["備註"] != (original["note"] or ""):
            update_data["note"] = row["備註"]

        if update_data:
            success = update_user(row["ID"], update_data)
            if success:
                update_count += 1

    st.success(f"✅ 成功更新 {update_count} 筆使用者資料。請重新整理頁面以查看變更。")

# 返回主頁按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")

logout_button()
