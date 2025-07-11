import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import requests
import pandas as pd

# 系統設定
st.set_page_config(page_title="帳號管理", layout="wide")
st.title("\U0001F464 帳號管理")

# 設定 API 埠域
API_BASE = "https://ocr-whisper-production-2.up.railway.app"

# --- 上方功能 ---

# 取得所有用戶
def get_users():
    try:
        response = requests.get(f"{API_BASE}/users")
        return response.json()
    except:
        return []

# 更新備註
def update_note(user_id, new_note):
    requests.put(f"{API_BASE}/users/{user_id}/note", json={"note": new_note})

# 啟用帳號
def activate_user(user_id):
    requests.put(f"{API_BASE}/users/{user_id}/activate")

# 停用帳號
def deactivate_user(user_id):
    requests.put(f"{API_BASE}/users/{user_id}/deactivate")

# 修改用戶認證資格 (例如管理員)
def update_admin_status(user_id, is_admin):
    requests.put(f"{API_BASE}/users/{user_id}/admin", json={"is_admin": is_admin})

# --- 主畫面 ---

with st.container():
    st.subheader("\u6240\u6709\u7528\u6236\u5e33\u865f (\u53ef\u4e92\u52d5)")
    users = get_users()

    if users:
        df = pd.DataFrame(users)
        df['is_admin'] = df['is_admin'].apply(lambda x: '✅ 是' if x else '❌ 否')
        df['is_active'] = df['is_active'].apply(lambda x: '🟢 啟用中' if x else '🔴 停用中')

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
        gb.configure_column("note", header_name="備註說明", editable=True)
        gb.configure_column("is_active", header_name="帳號狀態", editable=False)
        gb.configure_column("is_admin", header_name="是否為管理員", editable=False)
        gb.configure_selection("single")

        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MANUAL,
            fit_columns_on_grid_load=True,
            height=300,
            theme="streamlit"
        )

        selected = grid_response['selected_rows']
        updated_df = grid_response['data']

        # 備註修改按鈕
        if st.button("📃 儲存備註修改"):
            for _, row in updated_df.iterrows():
                update_note(row['id'], row['note'])
            st.success("備註已更新！")

        # 如果有選擇單一名用戶
        if selected:
            selected_user = selected[0]
            st.divider()
            st.subheader("⚙️ 編輯選定帳號")
            col1, col2 = st.columns(2)

            with col1:
                # 啟用 / 停用按鈕
                if selected_user['is_active'] == '🔴 停用中':
                    if st.button("✅ 啟用帳號"):
                        activate_user(selected_user['id'])
                        st.success("帳號已啟用")
                else:
                    if st.button("⛔ 停用帳號"):
                        deactivate_user(selected_user['id'])
                        st.warning("帳號已停用")

            with col2:
                # 修改是否為管理員
                admin_toggle = st.selectbox("修改使用者身份：", ["使用者", "管理員"], index=1 if selected_user['is_admin'] == '✅ 是' else 0)
                is_admin = True if admin_toggle == "管理員" else False

                if st.button("✏️ 更新使用者身份"):
                    update_admin_status(selected_user['id'], is_admin)
                    st.success("使用者身份已更新")

    else:
        st.warning("查無使用者資料。")

# --- 返回 ---
st.markdown("---")
if st.button("🔙 返回首頁"):
    st.switch_page("首頁.py")
