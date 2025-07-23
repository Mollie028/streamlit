import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="帳號管理", page_icon="👥")

# ====== 登入檢查與登出 ======
from utils.auth import is_logged_in, logout_button

if not is_logged_in():
    st.error("請先登入以使用本頁面。")
    st.stop()

logout_button()
# ============================

st.markdown("## 👥 帳號管理")
st.markdown("### 使用者帳號列表")

backend_url = "https://ocr-whisper-production-2.up.railway.app"

# 取得使用者列表
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
        update_mode=GridUpdateMode.MANUAL,
        allow_unsafe_jscode=True,
        theme="streamlit",
        height=380,
        fit_columns_on_grid_load=True,
    )

    updated_rows = grid_response["data"]
    edited_df = pd.DataFrame(updated_rows)

    st.markdown("#### 📥 點選表格進行編輯，完成後按下「儲存變更」")

    if st.button("💾 儲存變更"):
        for idx, row in edited_df.iterrows():
            user_id = row["ID"]
            original = df[df["ID"] == user_id].iloc[0]

            # 狀態處理
            if row["使用者狀況"] != original["使用者狀況"]:
                action = row["使用者狀況"]
                if action == "啟用":
                    requests.put(f"{backend_url}/enable_user/{user_id}", headers={"Authorization": f"Bearer {st.session_state['access_token']}"})
                elif action == "停用":
                    requests.put(f"{backend_url}/disable_user/{user_id}", headers={"Authorization": f"Bearer {st.session_state['access_token']}"})
                elif action == "刪除":
                    requests.delete(f"{backend_url}/delete_user/{user_id}", headers={"Authorization": f"Bearer {st.session_state['access_token']}"})

            # 備註更新
            if row["備註"] != original["備註"]:
                requests.put(
                    f"{backend_url}/update_user/{user_id}",
                    json={"note": row["備註"]},
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )

        st.success("✅ 已成功儲存所有變更！")
        st.cache_data.clear()
        st.rerun()
else:
    st.info("目前尚無使用者資料。")
