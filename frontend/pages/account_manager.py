import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import requests

API_URL = "https://ocr-whisper-production-2.up.railway.app"

def run():
    st.markdown("### 👤 帳號管理")
    st.markdown("#### 📋 使用者清單")

    # 🔒 權限檢查
    if "user" not in st.session_state:
        st.error("⚠️ 請先登入")
        st.stop()

    if not st.session_state.get("is_admin", False):
        st.warning("⛔️ 您沒有權限查看此頁面")
        st.stop()

    # ✅ 取得使用者資料
    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        users = res.json()
    except Exception as e:
        st.error(f"❌ 無法載入使用者資料：{e}")
        return

    # ✅ 整理表格資料
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

    # ✅ 建立 AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("single", use_checkbox=True)
    gb.configure_column("帳號名稱", editable=False)
    gb.configure_column("是否為管理員", editable=False)
    gb.configure_column("啟用狀態", editable=False)
    gb.configure_column("備註", editable=False)
    gb.configure_column("使用者ID", editable=False)

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=520,  # ✅ 放大表格高度
        width='100%',
        theme="streamlit"
    )

    selected = grid["selected_rows"]
    if selected:
        row = selected[0]
        user_id = row["使用者ID"]
        username = row["帳號名稱"]
        current_status = row["啟用狀態"]

        st.markdown("#### 🔧 帳號操作")
        st.write(f"🆔 使用者 ID：{user_id}")
        st.write(f"👤 帳號名稱：{username}")
        st.write(f"🔒 狀態：{current_status}")

        # ✅ 下拉選單
        if current_status == "啟用中":
            action = st.selectbox("請選擇操作", ["停用帳號", "刪除帳號"])
        else:
            action = st.selectbox("請選擇操作", ["啟用帳號", "刪除帳號"])

        if st.button("✅ 執行操作"):
            try:
                if action == "停用帳號":
                    res = requests.post(f"{API_URL}/disable_user/{user_id}")
                elif action == "啟用帳號":
                    res = requests.post(f"{API_URL}/enable_user/{user_id}")
                elif action == "刪除帳號":
                    res = requests.delete(f"{API_URL}/delete_user/{user_id}")
                else:
                    st.warning("⚠️ 未知操作")
                    return

                if res.status_code == 200:
                    st.success("✅ 操作成功，請重新整理頁面")
                else:
                    st.error(f"❌ 操作失敗：{res.text}")
            except Exception as e:
                st.error(f"❌ 操作失敗：{e}")

    # ✅ 返回按鈕
    st.markdown("---")
    if st.button("🔙 返回主畫面"):
        st.switch_page("app.py")
