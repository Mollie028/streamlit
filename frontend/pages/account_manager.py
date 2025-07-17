import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.stylable_container import stylable_container

API_URL = "https://ocr-whisper-production-2.up.railway.app"

st.set_page_config(page_title="帳號管理", page_icon="👩‍💼", layout="wide")
st.markdown("## 👩‍💼 帳號管理")

# 🧩 限管理員才能進入
current_user = st.session_state.get("user_info", {})
if not current_user.get("is_admin", False):
    st.warning("此頁面僅限管理員使用")
    st.stop()

# 📦 抓取使用者資料
def fetch_users():
    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"無法取得使用者資料：{e}")
        return []

# 🔧 處理使用者資料
def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df
    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "company_name": "公司名稱",
        "is_admin": "是否為管理員",
        "is_active": "啟用狀態",
        "note": "備註"
    })
    df["是否為管理員"] = df["是否為管理員"].astype(bool)
    df["啟用狀態"] = df["啟用狀態"].astype(bool)
    df["狀態"] = df["啟用狀態"].apply(lambda x: "啟用中" if x else "已停用")
    return df

# 🚀 載入與顯示帳號表格
users = fetch_users()
df = process_users(users)

if df.empty:
    st.info("尚無有效使用者資料")
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("single", use_checkbox=True)
    gb.configure_column("是否為管理員", editable=False)
    gb.configure_column("啟用狀態", hide=True)
    grid_response = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode="SELECTION_CHANGED",
        theme="streamlit",
        height=400,
        fit_columns_on_grid_load=True
    )

selected_rows = grid_response["selected_rows"]

with col2:
    st.subheader("⚙️ 帳號操作區")

    if not selected_rows:
        st.info("請點選左側帳號以進行操作")
    else:
        selected = selected_rows[0]
        user_id = selected["使用者ID"]
        username = selected["帳號名稱"]
        is_active = selected["啟用狀態"]

        st.markdown(f"**帳號 ID：** `{user_id}`")
        st.markdown(f"**帳號名稱：** `{username}`")
        st.markdown(f"**目前狀態：** `{'啟用中' if is_active else '已停用'}`")

        actions = []
        if is_active:
            actions = ["停用帳號", "刪除帳號"]
        else:
            actions = ["啟用帳號", "刪除帳號"]

        action = st.radio("選擇操作動作：", actions, horizontal=True)

        if st.button("✅ 執行操作"):
            try:
                if action == "啟用帳號":
                    requests.put(f"{API_URL}/enable_user/{user_id}")
                    st.success("帳號已啟用")
                elif action == "停用帳號":
                    requests.put(f"{API_URL}/disable_user/{user_id}")
                    st.success("帳號已停用")
                elif action == "刪除帳號":
                    requests.delete(f"{API_URL}/delete_user/{user_id}")
                    st.success("帳號已刪除")
                st.rerun()
            except Exception as e:
                st.error(f"執行失敗：{e}")

# 🔙 返回主頁
with stylable_container("back", css_styles="margin-top: 20px"):
    if st.button("🔙 返回主頁"):
        st.session_state["current_page"] = "home"
        st.rerun()

# ✅ run() 支援 app.py 呼叫
def run():
    pass
