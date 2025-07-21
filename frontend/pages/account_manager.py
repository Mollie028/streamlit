import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="帳號管理", layout="wide")
st.title("🔐 帳號管理")

API_URL = "https://ocr-whisper-production-2.up.railway.app"

def fetch_users():
    try:
        response = requests.get(f"{API_URL}/users")
        return response.json()
    except Exception as e:
        st.error(f"無法取得使用者資料：{e}")
        return []

def update_user(user_id, updated_data):
    try:
        res = requests.put(f"{API_URL}/update_user/{user_id}", json=updated_data)
        return res.status_code == 200
    except:
        return False

def change_password(user_id, new_password):
    try:
        res = requests.put(f"{API_URL}/update_user_password/{user_id}", json={"new_password": new_password})
        return res.status_code == 200
    except:
        return False

def action_menu(user, is_admin):
    options = []
    if user.get("is_active"):
        options.append("停用帳號")
    else:
        options.append("啟用帳號")
    options.append("刪除帳號")
    options.append("修改密碼")
    if user.get("is_admin"):
        options = ["不可操作管理員"]

    action = st.selectbox("選擇操作", options, key=f"action_{user['id']}")

    if action == "修改密碼":
        new_pwd = st.text_input("輸入新密碼", type="password", key=f"pwd_{user['id']}")
        if st.button("確認修改", key=f"btn_pwd_{user['id']}"):
            if change_password(user['id'], new_pwd):
                st.success("✅ 密碼修改成功")
            else:
                st.error("❌ 修改失敗")

    elif action == "停用帳號" and not user.get("is_admin"):
        if st.button("確認停用", key=f"disable_{user['id']}"):
            if update_user(user['id'], {"is_active": False}):
                st.success("✅ 帳號已停用")

    elif action == "啟用帳號" and not user.get("is_admin"):
        if st.button("確認啟用", key=f"enable_{user['id']}"):
            if update_user(user['id'], {"is_active": True}):
                st.success("✅ 帳號已啟用")

    elif action == "刪除帳號" and not user.get("is_admin"):
        if st.button("⚠️ 確認刪除", key=f"delete_{user['id']}"):
            res = requests.delete(f"{API_URL}/delete_user/{user['id']}")
            if res.status_code == 200:
                st.success("✅ 帳號已刪除")
            else:
                st.error("❌ 刪除失敗")

# 搜尋功能
search_keyword = st.text_input("🔍 請輸入帳號名稱或 ID 搜尋：")

# 顯示使用者資料表格
users_data = fetch_users()
if users_data:
    if search_keyword:
        users_data = [u for u in users_data if search_keyword.lower() in str(u.get("username", "")).lower() or search_keyword in str(u.get("id", ""))]

    gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(users_data))
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, resizable=True, wrapText=True, autoHeight=True)
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(pd.DataFrame(users_data), gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED, height=380)

    selected = grid_response["selected_rows"]
    if selected:
        st.subheader("✏️ 帳號操作區")
        selected_user = selected[0]
        action_menu(selected_user, selected_user.get("is_admin"))
else:
    st.warning("⚠️ 尚無帳號資料")
