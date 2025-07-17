import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import requests

def run():
    st.title("👤 帳號管理")

    if st.button("🔙 登出"):
        st.session_state.clear()
        st.success("✅ 已登出，請重新整理畫面")
        return

    # ➤ 基本資訊
    api_base = "https://ocr-whisper-production-2.up.railway.app"
    current_user = st.session_state.get("user", {})
    is_admin = current_user.get("is_admin", False)
    current_username = current_user.get("username", "")

    # ➤ 取得使用者資料
    res = requests.get(f"{api_base}/users")
    if res.status_code != 200:
        st.error("❌ 無法取得帳號資料")
        return
    users = res.json()

    # ➤ 搜尋欄位
    keyword = st.text_input("🔍 搜尋使用者 ID 或帳號名稱")

    # ➤ 整理成 DataFrame
    df_raw = []
    for u in users:
        df_raw.append({
            "user_id": u["id"],
            "username": u["username"],
            "is_admin": u["is_admin"],
            "status": "啟用中" if u["is_active"] else "已停用",
            "note": u.get("note", "")
        })
    df = pd.DataFrame(df_raw)

    # ➤ 關鍵字過濾
    if keyword:
        df = df[
            df["user_id"].astype(str).str.contains(keyword) |
            df["username"].str.contains(keyword)
        ]

    if df.empty:
        st.warning("查無符合條件的帳號")
        return

    # ➤ 顯示 AgGrid 表格
    st.subheader("📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True, use_checkbox_for_row=True)
    gb.configure_column("note", editable=True, header_name="備註")
    gb.configure_column("user_id", header_name="使用者ID", width=90)
    gb.configure_column("username", header_name="帳號名稱", width=130)
    gb.configure_column("is_admin", header_name="是否為管理員", width=130)
    gb.configure_column("status", header_name="啟用狀態", width=110)
    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=380,
        fit_columns_on_grid_load=True,
        theme="streamlit"
    )

    selected_df = pd.DataFrame(grid["selected_rows"])
    edited_df = grid["data"]

    # ➤ 處理多筆選取操作
    if not selected_df.empty:
        st.markdown("---")
        st.subheader("🔧 批次帳號操作")

        selected_ids = selected_df["user_id"].tolist()
        selected_usernames = selected_df["username"].tolist()

        if not is_admin and any(name != current_username for name in selected_usernames):
            st.error("⛔ 非管理員僅能操作自己帳號")
            return

        action = st.selectbox("請選擇操作", ["啟用帳號", "停用帳號", "刪除帳號", "修改密碼"])

        if action == "修改密碼":
            new_pw = st.text_input("🔑 請輸入新密碼", type="password")
            if not new_pw:
                st.warning("請輸入新密碼")
                return

        if st.button("✅ 執行操作"):
            success = 0
            for uid in selected_ids:
                if action == "啟用帳號":
                    r = requests.post(f"{api_base}/enable_user/{uid}")
                elif action == "停用帳號":
                    r = requests.post(f"{api_base}/disable_user/{uid}")
                elif action == "刪除帳號":
                    r = requests.delete(f"{api_base}/delete_user/{uid}")
                elif action == "修改密碼":
                    r = requests.put(f"{api_base}/update_user_password/{uid}", json={"new_password": new_pw})
                else:
                    continue
                if r.status_code == 200:
                    success += 1
            st.success(f"✅ 已成功操作 {success} 筆帳號")

    # ➤ 儲存備註欄位
    if st.button("💾 儲存備註變更"):
        success = 0
        for index, row in pd.DataFrame(edited_df).iterrows():
            uid = row["user_id"]
            note = row["note"]
            r = requests.put(f"{api_base}/update_user/{uid}", json={"note": note})
            if r.status_code == 200:
                success += 1
        st.success(f"📝 備註已更新 {success} 筆")
