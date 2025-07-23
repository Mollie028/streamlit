import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode
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

    if not is_logged_in():
        st.error("請先登入以使用本頁面。")
        st.stop()
    logout_button()

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
            "備註": u["備註"],
            "修改密碼": ""
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
        gb.configure_column("修改密碼", header_name="🔐 修改密碼", width=120,
                            cellRenderer=JsCode("""
                                function(params) {
                                    return `<button style='padding:4px 8px;'>修改</button>`;
                                }
                            """))

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

        st.markdown("#### 📅 點選表格進行編輯，完成後按下「儲存變更」")

        if st.button("儲存變更"):
            change_count = 0
            for i in range(len(df)):
                old_row = df.iloc[i]
                new_row = edited_df.iloc[i]

                if (
                    old_row["使用者狀況"] != new_row["使用者狀況"]
                    or old_row["是否為管理員"] != new_row["是否為管理員"]
                    or old_row["備註"] != new_row["備註"]
                ):
                    user_id = new_row["ID"]
                    updated_data = {
                        "note": str(new_row["備註"]) if pd.notna(new_row["備註"]) else "",
                        "is_admin": bool(new_row["是否為管理員"]),
                        "is_active": True if new_row["使用者狀況"] == "啟用" else False
                    }
                    if update_user(user_id, updated_data):
                        change_count += 1

            if change_count > 0:
                st.success(f"✅ 成功儲存 {change_count} 筆變更")
            else:
                st.info("沒有資料變更")

        # ✅ 密碼修改區塊
        selected_row = grid_response["selected_rows"]
        if selected_row:
            selected_user = selected_row[0]
            with st.expander(f"🔐 修改密碼 - {selected_user['使用者帳號']}（ID: {selected_user['ID']}）", expanded=True):
                new_pwd = st.text_input("新密碼", type="password", key="new_pwd")
                confirm_pwd = st.text_input("確認新密碼", type="password", key="confirm_pwd")
                current_user = is_logged_in()
                old_pwd = None

                # 登入者本人需驗證舊密碼
                if current_user and current_user["username"] == selected_user["使用者帳號"]:
                    old_pwd = st.text_input("舊密碼（本人驗證）", type="password", key="old_pwd")

                if st.button("✅ 確認修改密碼"):
                    if not new_pwd or not confirm_pwd:
                        st.warning("請輸入新密碼與確認密碼")
                    elif new_pwd != confirm_pwd:
                        st.warning("新密碼與確認密碼不一致")
                    else:
                        payload = {"new_password": new_pwd}
                        if old_pwd:
                            payload["old_password"] = old_pwd

                        try:
                            res = requests.put(
                                f"{backend_url}/update_user_password/{selected_user['ID']}",
                                json=payload,
                                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                            )
                            if res.status_code == 200:
                                st.success("✅ 密碼修改成功")
                            else:
                                st.error(f"❌ 更新失敗：{res.text}")
                        except Exception as e:
                            st.error(f"❌ 請求錯誤：{e}")

    # 👉 底部功能列：返回首頁 + 登出
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 返回首頁"):
            st.session_state["current_page"] = "home"
            st.rerun()
    with col2:
        if st.button("🔒 登出"):
            st.session_state.clear()
            st.session_state["current_page"] = "login"
            st.rerun()
