import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import requests

# ✅ run() 支援 app.py 呼叫
def run():
    st.title("👤 帳號管理")

    # ✅ 登出按鈕
    if st.button("🔙 登出"):
        st.session_state.clear()
        st.success("✅ 已登出，請重新整理頁面")
        return

    # ✅ 基本資訊
    api_base = "https://ocr-whisper-production-2.up.railway.app"
    current_user = st.session_state.get("user", {})
    is_admin = current_user.get("is_admin", False)
    current_username = current_user.get("username", "")

    # ✅ 取得使用者資料
    res = requests.get(f"{api_base}/users")
    if res.status_code != 200:
        st.error("❌ 無法取得帳號資料")
        return
    users = res.json()

    # ✅ 搜尋欄位
    keyword = st.text_input("🔍 搜尋使用者 ID 或帳號名稱")

    # ✅ 整理成 DataFrame
    df_raw = []
    for u in users:
        df_raw.append({
            "使用者ID": u["id"],
            "帳號名稱": u["username"],
            "是否為管理員": "✅" if u["is_admin"] else "",
            "啟用狀態": "啟用中" if u["is_active"] else "已停用",
            "備註": u.get("note", "")
        })
    df = pd.DataFrame(df_raw)

    # ✅ 關鍵字過濾
    if keyword:
        df = df[df["使用者ID"].astype(str).str.contains(keyword) | df["帳號名稱"].str.contains(keyword)]

    if df.empty:
        st.warning("查無符合條件的帳號")
        return

    # ✅ 顯示 AgGrid 表格
    st.subheader("📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)
    for col in ["備註"]:
        gb.configure_column(col, editable=True)
    grid_response = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode="MODEL_CHANGED",
        height=380,
        theme="streamlit"
    )
    selected_rows = grid_response["selected_rows"]
    edited_rows = grid_response["data"]

    if selected_rows:
        st.markdown("---")
        st.subheader("🔧 批次帳號操作")

        selected_ids = [r["使用者ID"] for r in selected_rows]
        selected_usernames = [r["帳號名稱"] for r in selected_rows]

        # ✅ 權限檢查：非管理員只能操作自己
        if not is_admin and any(u != current_username for u in selected_usernames):
            st.error("⛔ 非管理員僅能操作自己帳號")
            return

        # ✅ 選擇操作
        action = st.selectbox("請選擇操作", ["啟用帳號", "停用帳號", "刪除帳號", "修改密碼"])

        # ✅ 密碼欄位
        if action == "修改密碼":
            new_pw = st.text_input("🔑 請輸入新密碼", type="password")
            if not new_pw:
                st.warning("請輸入新密碼")
                return

        # ✅ 執行按鈕
        if st.button("✅ 執行操作"):
            success_count = 0
            for user_id in selected_ids:
                if action == "啟用帳號":
                    r = requests.post(f"{api_base}/enable_user/{user_id}")
                elif action == "停用帳號":
                    r = requests.post(f"{api_base}/disable_user/{user_id}")
                elif action == "刪除帳號":
                    r = requests.delete(f"{api_base}/delete_user/{user_id}")
                elif action == "修改密碼":
                    r = requests.put(f"{api_base}/update_user_password/{user_id}", json={"new_password": new_pw})
                else:
                    continue

                if r.status_code == 200:
                    success_count += 1

            st.success(f"✅ 已成功操作 {success_count} 筆帳號，請重新整理畫面")

    # ✅ 儲存備註欄位變更
    if st.button("💾 儲存備註變更"):
        updated_notes = edited_rows[["使用者ID", "備註"]]
        success = 0
        for _, row in updated_notes.iterrows():
            user_id = row["使用者ID"]
            note = row["備註"]
            r = requests.put(f"{api_base}/update_user/{user_id}", json={"note": note})
            if r.status_code == 200:
                success += 1
        st.success(f"📝 備註已更新 {success} 筆")
