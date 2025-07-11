import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from core.config import API_BASE

st.set_page_config(page_title="帳號管理", page_icon="👥", layout="wide")

def run():
    st.title("👥 帳號管理")

    # 🔐 取得使用者清單
    try:
        res = requests.get(
            f"{API_BASE}/users",
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        if res.status_code != 200:
            st.error("⚠️ 無法取得使用者資料")
            return

        users = res.json()
        df = pd.DataFrame(users)

        # ✅ 顯示可編輯的表格
        df_display = df.rename(columns={
            "id": "使用者編號",
            "username": "使用者帳號",
            "is_admin": "是否為管理員",
            "company_name": "公司名稱",
            "note": "備註說明",
            "is_active": "帳號狀態"
        })

        df_display["是否為管理員"] = df_display["是否為管理員"].apply(lambda x: "✅ 是" if x else "❌ 否")
        df_display["帳號狀態"] = df_display["帳號狀態"].apply(lambda x: "🟢 啟用中" if x else "⛔ 停用")

        st.markdown("### 所有使用者帳號（可互動）")

        gb = GridOptionsBuilder.from_dataframe(df_display)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
        gb.configure_column("使用者帳號", editable=False)
        gb.configure_column("是否為管理員", editable=False)
        gb.configure_column("帳號狀態", editable=False)
        gb.configure_column("使用者編號", editable=False)
        gb.configure_column("公司名稱", editable=False)
        grid_options = gb.build()

        grid_response = AgGrid(
            df_display,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MANUAL,
            height=300,
            allow_unsafe_jscode=True,
            use_container_width=True
        )

        edited_rows = grid_response["data"]
        selected = grid_response["selected_rows"]

        # 🔄 提交備註修改
        if st.button("💾 儲存備註修改"):
            for i, row in edited_rows.iterrows():
                user_id = df.loc[i, "id"]
                note = row["備註說明"]
                try:
                    requests.put(
                        f"{API_BASE}/update_note/{user_id}",
                        json={"note": note},
                        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                    )
                except Exception as e:
                    st.error(f"❌ 更新失敗：{e}")
            st.success("✅ 備註已更新！")
            st.rerun()

        st.markdown("---")
        st.markdown("### 🔧 管理帳號")

        # 🔍 選擇要管理的帳號（下拉選單）
        username_list = df["username"].tolist()
        selected_username = st.selectbox("請選擇要管理的使用者帳號", username_list)

        selected_user = df[df["username"] == selected_username].iloc[0]

        st.markdown(f"👤 **{selected_username}**（{'管理員' if selected_user['is_admin'] else '使用者'}）")

        # ✏️ 修改密碼
        new_password = st.text_input("輸入新密碼", type="password")
        if st.button("✅ 修改密碼"):
            try:
                res = requests.put(
                    f"{API_BASE}/update_password",
                    json={"username": selected_username, "new_password": new_password},
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )
                if res.status_code == 200:
                    st.success("✅ 密碼已更新")
                else:
                    st.error("❌ 密碼更新失敗")
            except Exception as e:
                st.error(f"🚨 發生錯誤：{e}")

        # 🔘 啟用／停用帳號
        current_status = "啟用中" if selected_user["is_active"] else "已停用"
        toggle_label = "⛔ 停用帳號" if selected_user["is_active"] else "🟢 啟用帳號"
        if st.button(toggle_label):
            try:
                res = requests.put(
                    f"{API_BASE}/toggle_active/{selected_user['id']}",
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )
                if res.status_code == 200:
                    st.success("✅ 帳號狀態已更新")
                    st.rerun()
                else:
                    st.error("❌ 更新帳號狀態失敗")
            except Exception as e:
                st.error(f"🚨 發生錯誤：{e}")

    except Exception as e:
        st.error("🚨 系統錯誤")
        st.code(str(e))
