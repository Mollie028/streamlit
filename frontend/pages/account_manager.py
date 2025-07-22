import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def run():
    st.set_page_config(page_title="帳號管理", layout="wide")
    st.title("🔐 帳號管理")

    API_URL = "https://ocr-whisper-production-2.up.railway.app"

    def fetch_users():
        try:
            res = requests.get(f"{API_URL}/users")
            return res.json()
        except Exception as e:
            st.error(f"❌ 無法取得使用者資料：{e}")
            return []

    def update_user(user_id, data):
        try:
            res = requests.put(f"{API_URL}/update_user/{user_id}", json=data)
            return res.status_code == 200
        except:
            return False

    def delete_user(user_id):
        try:
            res = requests.delete(f"{API_URL}/delete_user/{user_id}")
            return res.status_code == 200
        except:
            return False

    search = st.text_input("🔍 輸入使用者帳號或 ID 查詢")
    data = fetch_users()

    if data:
        df = pd.DataFrame(data)

        if search:
            df = df[df["username"].str.contains(search) | df["id"].astype(str).str.contains(search)]

        columns_order = ["id", "username", "note", "company", "is_admin", "is_active"]
        df = df[columns_order]

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=False)
        gb.configure_column("note", editable=True)
        gb.configure_column("company", editable=True)
        gb.configure_column("is_admin", editable=True)
        gb.configure_column("is_active", editable=True)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gridOptions = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            height=380,
            allow_unsafe_jscode=True
        )

        new_df = pd.DataFrame(grid_response["data"])
        selected = grid_response.get("selected_rows", [])

        st.markdown("### ✏️ 欄位修改")
        if st.button("💾 儲存所有欄位修改"):
            changed_rows = 0
            for i in range(len(new_df)):
                original = df.iloc[i]
                updated = new_df.iloc[i]
                if not updated.equals(original):
                    payload = {
                        "note": updated["note"],
                        "company": updated["company"],
                        "is_admin": updated["is_admin"],
                        "is_active": updated["is_active"]
                    }
                    success = update_user(updated["id"], payload)
                    if success:
                        changed_rows += 1
            st.success(f"✅ 已更新 {changed_rows} 筆帳號資料")

        st.markdown("### 🔧 多筆帳號批次操作")
        if isinstance(selected, list) and len(selected) > 0:
            selected_ids = [row['id'] for row in selected if isinstance(row, dict) and not row.get("is_admin", False)]
            if selected_ids:
                action = st.selectbox("請選擇操作", ["啟用帳號", "停用帳號", "刪除帳號"])
                if st.button("執行操作"):
                    count = 0
                    for uid in selected_ids:
                        if action == "啟用帳號":
                            if update_user(uid, {"is_active": True}):
                                count += 1
                        elif action == "停用帳號":
                            if update_user(uid, {"is_active": False}):
                                count += 1
                        elif action == "刪除帳號":
                            if delete_user(uid):
                                count += 1
                    st.success(f"✅ 已完成 {action}，共 {count} 筆")
            else:
                st.warning("⚠️ 不可對管理員進行批次操作")
        else:
            st.info("請先選取要操作的帳號 ✅")
    else:
        st.warning("⚠️ 無法載入帳號資料")
