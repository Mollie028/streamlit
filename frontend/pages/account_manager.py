import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
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
        st.error(f"更新時發生錯誤：{e}")
        return False

def delete_user(user_id):
    try:
        response = requests.delete(
            f"{backend_url}/delete_user/{user_id}",
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"刪除錯誤：{e}")
        return False

def update_password(user_id, new_password, old_password=None):
    payload = {"new_password": new_password}
    if old_password:
        payload["old_password"] = old_password
    try:
        res = requests.put(
            f"{backend_url}/update_user_password/{user_id}",
            json=payload,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)

def run():
    st.set_page_config(page_title="帳號管理", page_icon="👥")

    if not is_logged_in():
        st.error("請先登入以使用本頁面。")
        st.stop()
    logout_button()

    st.markdown("## 👥 帳號管理")
    st.markdown("### 使用者帳號列表")

    current_user = st.session_state.get("user_info", {})
    is_admin = current_user.get("role") == "admin"

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
        gb.configure_column("是否為管理員", editable=False, width=100)

        status_options = ["啟用", "停用"]
        if is_admin:
            status_options.append("刪除")
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

                if new_row["使用者狀況"] == "刪除" and is_admin and current_user.get("username") != new_row["使用者帳號"]:
                    if delete_user(user_id):
                        st.success(f"✅ 已刪除帳號 {new_row['使用者帳號']}")
                        st.rerun()
                    else:
                        st.error(f"❌ 刪除失敗：{new_row['使用者帳號']}")
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

        selected = grid_response.get("selected_rows", [])
        if selected:
            selected_user = selected[0]
            st.markdown("---")
            st.markdown(f"### 🔒 修改密碼 - 使用者：{selected_user['使用者帳號']}")
            new_pwd = st.text_input("請輸入新密碼", type="password")
            confirm_pwd = st.text_input("再次確認新密碼", type="password")
            old_pwd = None

            if current_user.get("username") == selected_user["使用者帳號"]:
                old_pwd = st.text_input("請輸入舊密碼（僅本人）", type="password")

            if st.button("✅ 送出密碼修改"):
                if not new_pwd or not confirm_pwd:
                    st.warning("請填寫所有欄位")
                elif new_pwd != confirm_pwd:
                    st.warning("兩次密碼不一致")
                else:
                    ok, msg = update_password(selected_user["ID"], new_pwd, old_pwd)
                    if ok:
                        st.success("✅ 密碼修改成功")
                    else:
                        st.error(f"❌ 密碼修改失敗：{msg}")

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
