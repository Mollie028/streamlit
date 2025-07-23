import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import requests

st.set_page_config(page_title="帳號管理", page_icon="👥")

# ====== 加入登入檢查與登出按鈕 ======
def is_logged_in():
    return "access_token" in st.session_state and "user" in st.session_state

def logout_button():
    if st.button("🚪 登出"):
        st.session_state.clear()
        st.experimental_rerun()

if not is_logged_in():
    st.error("請先登入以使用本頁面。")
    st.stop()

logout_button()
# ====== 登入檢查區塊結束 ======

st.markdown("## 👥 帳號管理")
st.markdown("### 使用者帳號列表")

backend_url = "https://ocr-whisper-production-2.up.railway.app"

# 取得使用者列表
def get_user_list():
    try:
        response = requests.get(f"{backend_url}/users", headers={"Authorization": f"Bearer {st.session_state['access_token']}"})
        if response.status_code == 200:
            return response.json()
        else:
            st.error("無法取得使用者資料。")
            return []
    except Exception as e:
        st.error(f"發生錯誤：{e}")
        return []

# 顯示表格
users = get_user_list()
if users:
    for user in users:
        user["是否為管理員"] = user.get("is_admin", False)
        user["使用者狀況"] = "啟用" if user.get("is_active", False) else "停用"
        user["備註"] = user.get("note", "")

    df = [{
        "ID": u["id"],
        "使用者帳號": u["username"],
        "是否為管理員": u["是否為管理員"],
        "使用者狀況": u["使用者狀況"],
        "備註": u["備註"]
    } for u in users]

    gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(df))
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_column("是否為管理員", type=["booleanColumn"], editable=False)
    gb.configure_column("備註", editable=False)
    gb.configure_column("使用者狀況", editable=False)
    gb.configure_column("ID", editable=False)
    gb.configure_column("使用者帳號", editable=False)

    grid_options = gb.build()

    AgGrid(
        pd.DataFrame(df),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        theme="streamlit",
        fit_columns_on_grid_load=True,
        height=380,
    )
else:
    st.info("目前尚無使用者資料。")
