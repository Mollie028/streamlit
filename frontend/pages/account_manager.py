import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.stylable_container import stylable_container

# ✅ 登入者資料（可整合到 session）
login_user = st.session_state.get("account", None)
login_role = st.session_state.get("role", None)

# ✅ API 路徑（請依部署調整）
API_BASE = "https://ocr-whisper-production-2.up.railway.app"

def fetch_users():
    try:
        res = requests.get(f"{API_BASE}/users")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"無法取得使用者清單：{e}")
    return []

def update_user_password(user_id, new_password):
    return requests.put(f"{API_BASE}/update_user_password/{user_id}", json={"new_password": new_password})

def update_user(user_id, data):
    return requests.put(f"{API_BASE}/update_user/{user_id}", json=data)

def disable_user(user_id):
    return requests.put(f"{API_BASE}/disable_user/{user_id}")

def enable_user(user_id):
    return requests.put(f"{API_BASE}/enable_user/{user_id}")

def delete_user(user_id):
    return requests.delete(f"{API_BASE}/delete_user/{user_id}")

def run():
    st.page_link("app.py", label="🔒 登出", icon="🔙")
    st.markdown("## 👤 帳號管理")

    if login_role != "admin":
        st.warning("只有管理員可以存取此頁面")
        return

    all_users = fetch_users()

    # ✅ 資料預處理
    df = pd.DataFrame(all_users)
    if df.empty:
        st.info("目前沒有任何使用者")
        return

    df["是否為管理員"] = df["role"] == "admin"
    df["啟用狀態"] = df["is_active"].map({True: "啟用中", False: "已停用"})

    # ✅ 搜尋功能
    keyword = st.text_input("🔍 搜尋使用者帳號或 ID")
    if keyword:
        df = df[df["username"].str.contains(keyword, na=False) | df["id"].astype(str).str.contains(keyword)]

    # ✅ AgGrid 設定
    gb = GridOptionsBuilder.from_dataframe(df[["id", "username", "是否為管理員", "啟用狀態", "note"]])
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_column("note", editable=True)
    gb.configure_column("啟用狀態", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用中", "停用帳號", "刪除帳號"]})
    grid_options = gb.build()

    with stylable_container("table-container", css=".st-emotion-cache-1r6slb0 {height: 380px;}"):
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MANUAL,
            fit_columns_on_grid_load=True,
            height=380,
            reload_data=True,
        )

    selected_rows = grid_response["selected_rows"]
    if selected_rows:
        selected = selected_rows[0]
        user_id = selected["id"]
        username = selected["username"]

        st.markdown("---")
        st.subheader("🔧 帳號操作")
        st.write(f"👤 帳號：{username}")
        st.write(f"🆔 ID：{user_id}")
        st.write(f"🔒 狀態：{selected['啟用狀態']}")

        action = st.selectbox("請選擇操作", ["停用帳號", "啟用帳號", "刪除帳號", "修改密碼"])
        new_password = None
        if action == "修改密碼":
            new_password = st.text_input("請輸入新密碼", type="password")

        if st.button("✅ 執行操作"):
            if action == "停用帳號":
                res = disable_user(user_id)
            elif action == "啟用帳號":
                res = enable_user(user_id)
            elif action == "刪除帳號":
                res = delete_user(user_id)
            elif action == "修改密碼":
                if not new_password:
                    st.warning("請輸入新密碼")
                    return
                res = update_user_password(user_id, new_password)
            else:
                res = None

            if res and res.status_code == 200:
                st.success("操作成功！請重新整理頁面查看更新")
            else:
                st.error(f"操作失敗：{res.text if res else 'Unknown error'}")

    # ✅ 儲存備註與狀態變更
    if st.button("💾 儲存變更"):
        updated_rows = grid_response["data"]
        for index, row in updated_rows.iterrows():
            user_id = row["id"]
            note = row.get("note", "")
            status = row.get("啟用狀態", "啟用中")

            if status == "刪除帳號":
                delete_user(user_id)
            elif status == "停用帳號":
                disable_user(user_id)
            elif status == "啟用中":
                enable_user(user_id)

            update_user(user_id, {"note": note})

        st.success("所有變更已儲存！")

