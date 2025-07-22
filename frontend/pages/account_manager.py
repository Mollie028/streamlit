import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def run():
    st.set_page_config(page_title="帳號管理", layout="wide")
    st.title("🔐 帳號管理")

    API_URL = "https://ocr-whisper-production-2.up.railway.app"

    # ========== 後端互動邏輯 ==========
    def fetch_users():
        try:
            res = requests.get(f"{API_URL}/users")
            return res.json()
        except Exception as e:
            st.error(f"❌ 無法取得使用者資料：{e}")
            return []

    def update_user(user_id, updated_data):
        try:
            res = requests.put(f"{API_URL}/update_user/{user_id}", json=updated_data)
            return res.status_code == 200
        except:
            return False

    def update_user_password(user_id, new_password):
        try:
            res = requests.put(f"{API_URL}/update_user_password/{user_id}", json={"new_password": new_password})
            return res.status_code == 200
        except:
            return False

    def batch_update(users_df, original_df):
        changes = []
        for _, row in users_df.iterrows():
            original = original_df[original_df['id'] == row['id']].iloc[0]
            changed_fields = {}
            for field in ['note', 'company', 'is_admin', 'is_active']:
                if row[field] != original[field]:
                    changed_fields[field] = row[field]
            if changed_fields:
                changes.append((row['id'], changed_fields))

        for user_id, fields in changes:
            update_user(user_id, fields)
        return len(changes)

    def batch_action(user_ids, action):
        count = 0
        for uid in user_ids:
            if action == "啟用帳號":
                success = update_user(uid, {"is_active": True})
            elif action == "停用帳號":
                success = update_user(uid, {"is_active": False})
            elif action == "刪除帳號":
                res = requests.delete(f"{API_URL}/delete_user/{uid}")
                success = res.status_code == 200
            else:
                success = False
            if success:
                count += 1
        return count

    # ========== 主頁面邏輯 ==========
    search_keyword = st.text_input("🔍 搜尋帳號或 ID：")
    users_data = fetch_users()

    if users_data:
        df = pd.DataFrame(users_data)
        if search_keyword:
            df = df[df['username'].str.contains(search_keyword, case=False) | df['id'].astype(str).str.contains(search_keyword)]

        editable_fields = ['note', 'company', 'is_admin', 'is_active']
        gb = GridOptionsBuilder.from_dataframe(df)
        for col in editable_fields:
            gb.configure_column(col, editable=True)
        gb.configure_selection('multiple', use_checkbox=True)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        grid_options = gb.build()

        st.markdown("### 👥 使用者列表")
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            height=380,
            fit_columns_on_grid_load=True
        )

        edited_rows = grid_response["data"]
        selected = grid_response["selected_rows"]

        if st.button("💾 儲存所有欄位修改"):
            updated_count = batch_update(pd.DataFrame(edited_rows), df)
            st.success(f"✅ 已儲存 {updated_count} 筆變更")

        if selected:
            selected_ids = [row['id'] for row in selected if isinstance(row, dict) and not row.get("is_admin", False)]
            if selected_ids:
                st.markdown("### 🔧 批次操作")
                batch_opt = st.selectbox("選擇要執行的操作", ["啟用帳號", "停用帳號", "刪除帳號"])
                if st.button("執行批次操作"):
                    count = batch_action(selected_ids, batch_opt)
                    st.success(f"✅ 已對 {count} 筆帳號執行「{batch_opt}」操作")
            else:
                st.warning("⚠️ 已選取帳號中包含管理員，無法進行批次操作")
        else:
            st.info("ℹ️ 請先選取要操作的帳號")
    else:
        st.warning("⚠️ 尚無帳號資料")
