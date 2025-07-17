import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder

def run():
    st.title("👥 帳號管理")

    # 🔐 取得目前使用者資訊
    current_user = st.session_state.get("username", "")
    is_admin = st.session_state.get("is_admin", False)

    # ✅ 取得使用者清單
    api_url = "https://ocr-whisper-production-2.up.railway.app/users"
    res = requests.get(api_url)
    if res.status_code != 200:
        st.error("❌ 無法載入帳號清單")
        return

    users = res.json()
    if not users:
        st.warning("⚠️ 尚無帳號資料")
        return

    # 🧾 整理表格資料
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

    # 🔍 關鍵字搜尋
    keyword = st.text_input("🔎 搜尋使用者 ID 或帳號名稱", "")
    if keyword:
        df = df[df["帳號名稱"].str.contains(keyword, case=False) |
                df["使用者ID"].astype(str).str.contains(keyword)]

    if df.empty:
        st.warning("查無符合條件的使用者")
        return

    # 📋 顯示表格（AgGrid）
    st.subheader("📄 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_grid_options(domLayout='normal')
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    # 設定欄位寬度平均
    for col in df.columns:
        gb.configure_column(col, width=150)

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode="SELECTION_CHANGED",
        height=380,
        theme="streamlit"
    )

    selected_rows = grid_response["selected_rows"]
    if selected_rows is None or len(selected_rows) == 0:
        st.info("✅ 請勾選一筆以上帳號後進行操作")
        return

    # 🧑‍⚖️ 權限檢查（非管理員不可操作他人）
    for row in selected_rows:
        if not is_admin and row["帳號名稱"] != current_user:
            st.error("❌ 僅限管理員操作他人帳號")
            return

    st.divider()
    st.subheader("🛠️ 批次操作")

    action = st.selectbox("請選擇操作項目", ["啟用帳號", "停用帳號", "刪除帳號"])

    if st.button("🚀 執行操作"):
        success, fail = 0, 0
        for row in selected_rows:
            uid = row["使用者ID"]
            if action == "啟用帳號":
                resp = requests.post(f"{api_url}/enable_user/{uid}")
            elif action == "停用帳號":
                resp = requests.post(f"{api_url}/disable_user/{uid}")
            elif action == "刪除帳號":
                resp = requests.delete(f"{api_url}/delete_user/{uid}")
            else:
                continue

            if resp.status_code == 200:
                success += 1
            else:
                fail += 1

        if success:
            st.success(f"✅ 成功 {success} 筆")
        if fail:
            st.error(f"❌ 失敗 {fail} 筆")
        st.experimental_rerun()
