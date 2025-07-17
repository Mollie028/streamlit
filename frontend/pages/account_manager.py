import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import requests
import pandas as pd

def run():
    st.title("👤 帳號管理")

    # ✅ 從後端 API 取得使用者列表
    api_url = "https://ocr-whisper-production-2.up.railway.app/users"
    response = requests.get(api_url)
    if response.status_code != 200:
        st.error("❌ 無法取得使用者資料")
        return
    users = response.json()

    if not users:
        st.warning("⚠️ 目前尚無帳號資料")
        return

    # ✅ 整理資料表格
    df = []
    for u in users:
        df.append({
            "使用者ID": u["id"],
            "帳號名稱": u["username"],
            "是否為管理員": "✅" if u["is_admin"] else "",
            "啟用狀態": "啟用中" if u["is_active"] else "已停用",
            "備註": u.get("note", "")
        })
    df = pd.DataFrame(df)

    # ✅ 顯示帳號清單表格（使用 AgGrid）
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📋 使用者清單")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection("single", use_checkbox=True)
        gb.configure_column("啟用狀態", editable=False)
        gb.configure_column("是否為管理員", editable=False)
        gb.configure_column("帳號名稱", editable=False)
        gb.configure_column("使用者ID", editable=False)

        grid_options = gb.build()
        grid_options["rowSelection"] = "single"

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode="SELECTION_CHANGED",
            height=400,
            theme="streamlit"
        )

    # ✅ 顯示選取帳號詳細資訊與操作選單
    selected_rows = grid_response["selected_rows"]
    if selected_rows is not None and len(selected_rows) > 0:
        selected = pd.DataFrame(selected_rows).iloc[0]  # ✅ 修正錯誤點在這行

        with col2:
            st.subheader("🔧 帳號操作")
            st.write(f"👤 帳號：{selected['帳號名稱']}")
            st.write(f"🆔 ID：{selected['使用者ID']}")
            st.write(f"🔒 狀態：{selected['啟用狀態']}")

            current_status = selected["啟用狀態"]
            user_id = selected["使用者ID"]

            # ✅ 根據目前狀態提供操作選單
            if current_status == "啟用中":
                action = st.selectbox("請選擇操作", ["停用帳號", "刪除帳號"])
            else:
                action = st.selectbox("請選擇操作", ["啟用帳號", "刪除帳號"])

            if st.button("✅ 執行操作"):
                if action == "停用帳號":
                    res = requests.post(f"{api_url}/disable_user/{user_id}")
                elif action == "啟用帳號":
                    res = requests.post(f"{api_url}/enable_user/{user_id}")
                elif action == "刪除帳號":
                    res = requests.delete(f"{api_url}/delete_user/{user_id}")

                if res.status_code == 200:
                    st.success("✅ 操作成功，請重新整理頁面")
                else:
                    st.error(f"❌ 操作失敗：{res.text}"
