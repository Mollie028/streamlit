import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import requests
import pandas as pd

def run():
    st.title("👤 帳號管理")

    # 👉 取得目前登入者的資訊
    current_user = st.session_state.get("username", "")
    is_admin = st.session_state.get("is_admin", False)

    # 👉 取得使用者清單
    api_url = "https://ocr-whisper-production-2.up.railway.app/users"
    response = requests.get(api_url)
    if response.status_code != 200:
        st.error("❌ 無法取得使用者資料")
        return
    users = response.json()

    if not users:
        st.warning("⚠️ 目前尚無帳號資料")
        return

    # 👉 建立 DataFrame
    data = []
    for u in users:
        data.append({
            "使用者ID": u["id"],
            "帳號名稱": u["username"],
            "是否為管理員": "✅" if u["is_admin"] else "",
            "啟用狀態": "啟用中" if u["is_active"] else "已停用",
            "備註": u.get("note", "")
        })
    df = pd.DataFrame(data)

    # 👉 關鍵字搜尋
    keyword = st.text_input("🔍 搜尋使用者 ID 或帳號名稱", "")
    if keyword:
        df = df[df["帳號名稱"].str.contains(keyword, case=False) | df["使用者ID"].astype(str).str.contains(keyword)]

    if df.empty:
        st.warning("查無符合條件的使用者")
        return

    # 👉 顯示 AgGrid 表格
    st.subheader("📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)
    for col in ["啟用狀態", "是否為管理員", "帳號名稱", "使用者ID"]:
        gb.configure_column(col, editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode="SELECTION_CHANGED",
        height=380,
        theme="streamlit"
    )

    selected_rows = grid_response["selected_rows"]
    if not selected_rows:
        st.info("請勾選欲操作的使用者")
        return

    st.subheader("🔧 帳號操作")

    # 👉 顯示選取帳號資訊
    selected_df = pd.DataFrame(selected_rows)
    st.dataframe(selected_df[["使用者ID", "帳號名稱", "啟用狀態"]], use_container_width=True)

    # 👉 檢查權限（非管理員只能編輯自己）
    invalid = False
    if not is_admin:
        for _, row in selected_df.iterrows():
            if row["帳號名稱"] != current_user:
                invalid = True
                break
    if invalid:
        st.error("❌ 僅限管理員可操作他人帳號")
        return

    # 👉 批次操作選單
    actions = []
    for _, row in selected_df.iterrows():
        if row["啟用狀態"] == "啟用中":
            actions.append("停用帳號")
        else:
            actions.append("啟用帳號")
    actions.append("刪除帳號")

    action = st.selectbox("請選擇操作類型", list(set(actions)))

    if st.button("✅ 執行操作"):
        success, fail = 0, 0
        for _, row in selected_df.iterrows():
            uid = row["使用者ID"]
            if action == "啟用帳號":
                res = requests.post(f"{api_url}/enable_user/{uid}")
            elif action == "停用帳號":
                res = requests.post(f"{api_url}/disable_user/{uid}")
            elif action == "刪除帳號":
                res = requests.delete(f"{api_url}/delete_user/{uid}")
            else:
                res = None

            if res and res.status_code == 200:
                success += 1
            else:
                fail += 1

        if success:
            st.success(f"✅ {action} 成功：{success} 位使用者")
        if fail:
            st.error(f"❌ {action} 失敗：{fail} 位使用者")

        st.experimental_rerun()
