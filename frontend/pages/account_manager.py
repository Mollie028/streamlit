import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from services.auth_service import is_logged_in, logout_button

# ✅ 提到外層，避免作用域錯誤
backend_url = "https://ocr-whisper-production-2.up.railway.app"

def update_user(user_id, data):
    try:
        response = requests.put(
            f"{backend_url}/update_user/{user_id}",
            json=data,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        if response.status_code == 200:
            return True
        else:
            st.error(f"更新失敗（ID: {user_id}）：{response.text}")
            return False
    except Exception as e:
        st.error(f"更新時發生錯誤：{e}")
        return False

def run():
    st.set_page_config(page_title="帳號管理", page_icon="👥")

    # ====== 登入檢查與登出 ======
    if not is_logged_in():
        st.error("請先登入以使用本頁面。")
        st.stop()
    logout_button()
    # ============================

    st.markdown("## 👥 帳號管理")
    st.markdown("### 使用者帳號列表")

    @st.cache_data(ttl=60)
    def get_user_list():
        try:
            response = requests.get(
                f"{backend_url}/users",
                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error("無法取得使用者資料。")
                return []
        except Exception as e:
            st.error(f"發生錯誤：{e}")
            return []

    users = get_user_list()
    if users:
        for user in users:
            user["是否為管理員"] = user.get("is_admin", False)
            user["使用者狀況"] = "啟用" if user.get("is_active", False) else "停用"
            user["備註"] = user.get("note", "")

        df = pd.DataFrame([{
            "ID": u["id"],
            "使用者帳號": u["username"],
            "是否為管理員": u["是否為管理員"],
            "使用者狀況": u["使用者狀況"],
            "備註": u["備註"]
        } for u in users])

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(wrapText=True, autoHeight=True)

        gb.configure_column("ID", editable=False, pinned="left", width=80)
        gb.configure_column("使用者帳號", editable=False, pinned="left", width=160)
        gb.configure_column("是否為管理員", editable=False, width=100)
        gb.configure_column("使用者狀況", editable=True, cellEditor='agSelectCellEditor',
                            cellEditorParams={'values': ["啟用", "停用", "刪除"]}, width=100)
        gb.configure_column("備註", editable=True)

        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            allow_unsafe_jscode=True,
            theme="streamlit",
            height=380,
            fit_columns_on_grid_load=True,
            editable=True,
            single_click_edit=True,
            reload_data=True  # ✅ 幫助手機觸控生效
        )

        edited_df = pd.DataFrame(grid_response["data"])

        st.markdown("#### 📥 點選表格進行編輯，完成後按下「儲存變更」")

        if st.button("儲存變更"):
            change_count = 0
            for row_idx, row in edited_df.iterrows():
                original_row = df.iloc[row_idx]  # ✅ 用 iloc 比對整數 index
                if not row.equals(original_row):
                    user_id = row["ID"]
                    updated_data = {
                        "note": row["備註"],
                        "is_admin": row["是否為管理員"],
                        "is_active": row["使用者狀況"] == "啟用"
                    }
                    if update_user(user_id, updated_data):
                        change_count += 1
            if change_count > 0:
                st.success(f"✅ 成功儲存 {change_count} 筆變更")
            else:
                st.info("沒有資料變更")

    # 👉 底部功能列：返回首頁 + 登出
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 返回首頁"):
            st.session_state["current_page"] = "home"
            st.rerun()
    with col2:
        if st.button("🚪 登出"):
            st.session_state.clear()
            st.session_state["current_page"] = "login"
            st.rerun()
