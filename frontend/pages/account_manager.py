import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import requests
import pandas as pd

# ✅ run() 支援 app.py 呼叫
def run():
    st.title("👤 帳號管理")

    # ✅ 登出按鈕
    if st.button("🔙 登出"):
        st.session_state.clear()
        st.success("✅ 已登出，請重新整理頁面")
        return

    # ✅ 使用者身分（從 session 判斷）
    current_user = st.session_state.get("username", "")
    is_admin = st.session_state.get("is_admin", False)

    # ✅ 取得所有使用者資料
    api_base = "https://ocr-whisper-production-2.up.railway.app"
    res = requests.get(f"{api_base}/users")
    if res.status_code != 200:
        st.error("❌ 無法取得帳號資料")
        return
    users = res.json()

    # ✅ 搜尋欄位
    keyword = st.text_input("🔍 搜尋使用者 ID 或帳號名稱")

    # ✅ 整理 DataFrame
    df_data = []
    for u in users:
        df_data.append({
            "使用者ID": u["id"],
            "帳號名稱": u["username"],
            "是否為管理員": "✅" if u["is_admin"] else "",
            "啟用狀態": "啟用中" if u["is_active"] else "已停用",
            "備註": u.get("note", ""),
        })
    df = pd.DataFrame(df_data)

    # ✅ 權限檢查：非管理員只能看自己
    if not is_admin:
        df = df[df["帳號名稱"] == current_user]

    # ✅ 搜尋過濾
    if keyword:
        df = df[df["使用者ID"].astype(str).str.contains(keyword) | df["帳號名稱"].str.contains(keyword)]

    if df.empty:
        st.warning("查無符合條件的使用者")
        return

    # ✅ AgGrid 表格（多選 + 備註可編輯）
    st.subheader("📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)  # ✅ 修正版本
    gb.configure_column("備註", editable=True)
    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode="MODEL_CHANGED",
        theme="streamlit",
        fit_columns_on_grid_load=True,
        height=380
    )
    updated_df = grid["data"]
    selected_rows = grid["selected_rows"]

    # ✅ 操作按鈕區塊（僅限管理員）
    if is_admin:
        st.subheader("🔧 批次帳號操作")
        action = st.selectbox("請選擇操作類型", ["無", "啟用帳號", "停用帳號", "刪除帳號"])
        if st.button("✅ 執行操作"):
            if not selected_rows:
                st.warning("請至少選取一筆使用者")
                return
            success_count = 0
            for row in selected_rows:
                uid = row["使用者ID"]
                if action == "啟用帳號":
                    r = requests.post(f"{api_base}/enable_user/{uid}")
                elif action == "停用帳號":
                    r = requests.post(f"{api_base}/disable_user/{uid}")
                elif action == "刪除帳號":
                    r = requests.delete(f"{api_base}/delete_user/{uid}")
                else:
                    continue
                if r.status_code == 200:
                    success_count += 1
            st.success(f"✅ 成功執行 {action}：{success_count} 筆")

    # ✅ 儲存備註變更（全部欄位都更新）
    if st.button("💾 儲存備註變更"):
        update_count = 0
        for i, row in updated_df.iterrows():
            uid = row["使用者ID"]
            note = row["備註"]
            user = next((u for u in users if u["id"] == uid), None)
            if user and user.get("note", "") != note:
                r = requests.put(f"{api_base}/update_user/{uid}", json={"note": note})
                if r.status_code == 200:
                    update_count += 1
        st.success(f"✅ 已更新 {update_count} 筆備註")

