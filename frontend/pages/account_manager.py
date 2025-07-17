import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import requests
import pandas as pd

def run():
    st.title("👤 帳號管理")

    # ✅ 權限檢查（未登入 or 非管理員擋住）
    if "user" not in st.session_state or "is_admin" not in st.session_state:
        st.warning("⚠️ 請先登入")
        st.stop()
    if not st.session_state["is_admin"]:
        st.error("⛔️ 僅限管理員操作本頁面")
        st.stop()

    # ✅ 從 API 取得使用者列表
    api_url = "https://ocr-whisper-production-2.up.railway.app/users"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"❌ 無法取得使用者資料：{e}")
        return

    users = response.json()
    if not users:
        st.info("📭 尚無使用者資料")
        return

    # ✅ 整理資料表格格式
    df = pd.DataFrame([{
        "使用者ID": u["id"],
        "帳號名稱": u["username"],
        "是否為管理員": "✅" if u["is_admin"] else "",
        "啟用狀態": "啟用中" if u["is_active"] else "已停用",
        "備註": u.get("note", "")
    } for u in users])

    # ✅ 顯示帳號表格（AgGrid）
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📋 使用者清單")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection("single", use_checkbox=True)
        for col in ["使用者ID", "帳號名稱", "是否為管理員", "啟用狀態", "備註"]:
            gb.configure_column(col, editable=False)

        grid_options = gb.build()
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode="SELECTION_CHANGED",
            height=500,
            theme="streamlit"
        )

    # ✅ 帳號操作區塊（單筆操作）
    selected_rows = grid_response["selected_rows"]
    if selected_rows:
        selected = selected_rows[0]
        with col2:
            st.subheader("🔧 帳號操作")
            st.markdown(f"👤 帳號名稱：**{selected['帳號名稱']}**")
            st.markdown(f"🆔 使用者 ID：`{selected['使用者ID']}`")
            st.markdown(f"🔒 目前狀態：**{selected['啟用狀態']}**")

            user_id = selected["使用者ID"]
            current_status = selected["啟用狀態"]

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
                else:
                    st.warning("⚠️ 未選擇有效操作")
                    return

                if res.status_code == 200:
                    st.success("✅ 操作成功，請重新整理頁面以查看最新狀態")
                else:
                    st.error(f"❌ 操作失敗：{res.text}")
