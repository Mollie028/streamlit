import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode
from services.auth_service import is_logged_in, logout_button

backend_url = "https://ocr-whisper-production-2.up.railway.app"

def update_user(user_id, data):
    try:
        response = requests.put(
            f"{backend_url}/update_user/{user_id}",
            json=data,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"更新錯誤：{e}")
        return False

def update_password(user_id, new_pwd, old_pwd=None):
    try:
        payload = {"new_password": new_pwd}
        if old_pwd:
            payload["old_password"] = old_pwd

        res = requests.put(
            f"{backend_url}/update_user_password/{user_id}",
            json=payload,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)

def delete_user(user_id):
    try:
        res = requests.delete(
            f"{backend_url}/delete_user/{user_id}",
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)

def run():
    st.set_page_config(page_title="帳號管理", page_icon="👥")

    user_info = is_logged_in()
    if not user_info:
        st.error("請先登入以使用本頁面。")
        st.stop()
    logout_button()

    is_admin = user_info.get("role") == "admin"

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
            return []
        except Exception as e:
            st.error(f"取得使用者失敗：{e}")
            return []

    users = get_user_list()
    if users:
        for user in users:
            user["是否為管理員"] = bool(user.get("is_admin", False))
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
        gb.configure_column("是否為管理員", editable=is_admin, cellEditor='agSelectCellEditor',
                            cellEditorParams={'values': [True, False]}, width=100)

        # ✅ 決定下拉選單項目
        if is_admin:
            status_options = ["啟用", "停用", "刪除"]
        else:
            status_options = ["啟用", "停用"]

        gb.configure_column("使用者狀況", editable=True, cellEditor='agSelectCellEditor',
                            cellEditorParams={'values': status_options}, width=100)
        gb.configure_column("備註", editable=True)

        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            theme="streamlit",
            height=380,
            fit_columns_on_grid_load=True,
            editable=True,
            single_click_edit=True,
            reload_data=True
        )

        edited_df = pd.DataFrame(grid_response["data"])

        st.markdown("#### 📥 點選表格進行編輯，完成後按下「儲存變更」")

        if st.button("儲存變更"):
            change_count = 0
            for i in range(len(df)):
                old_row = df.iloc[i]
                new_row = edited_df.iloc[i]
                user_id = new_row["ID"]

                if new_row["使用者狀況"] == "刪除":
                    if is_admin and user_info["username"] != new_row["使用者帳號"]:
                        success, msg = delete_user(user_id)
                        if success:
                            st.success(f"✅ 已刪除帳號 {new_row['使用者帳號']}")
                            st.rerun()
                        else:
                            st.error(f"❌ 刪除失敗：{msg}")
                    continue

                if (
                    old_row["使用者狀況"] != new_row["使用者狀況"]
                    or old_row["是否為管理員"] != new_row["是否為管理員"]
                    or old_row["備註"] != new_row["備註"]
                ):
                    updated_data = {
                        "note": str(new_row["備註"]) if pd.notna(new_row["備註"]) else "",
                        "is_admin": bool(new_row["是否為管理員"]),
                        "is_active": new_row["使用者狀況"] == "啟用"
                    }
                    if update_user(user_id, updated_data):
                        change_count += 1

            if change_count > 0:
                st.success(f"✅ 成功儲存 {change_count} 筆變更")
            else:
                st.info("沒有資料變更")

        selected_row = grid_response["selected_rows"]
        if selected_row:
            selected_user = selected_row[0]
            with st.expander(f"🔒 修改密碼 - {selected_user['使用者帳號']}（ID: {selected_user['ID']}）", expanded=True):
                new_pwd = st.text_input("新密碼", type="password", key="new_pwd")
                confirm_pwd = st.text_input("確認新密碼", type="password", key="confirm_pwd")
                old_pwd = None

                if user_info["username"] == selected_user["使用者帳號"]:
                    old_pwd = st.text_input("舊密碼", type="password", key="old_pwd")

                if st.button("✅ 送出修改密碼"):
                    if not new_pwd or not confirm_pwd:
                        st.warning("請填寫新密碼與確認密碼")
                    elif new_pwd != confirm_pwd:
                        st.warning("兩次密碼不一致")
                    else:
                        success, msg = update_password(selected_user["ID"], new_pwd, old_pwd)
                        if success:
                            st.success("✅ 密碼修改成功")
                        else:
                            st.error(f"❌ 修改失敗：{msg}")

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
