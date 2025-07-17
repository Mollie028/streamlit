import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
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

    # ✅ 取得使用者資料
    api_base = "https://ocr-whisper-production-2.up.railway.app"
    res = requests.get(f"{api_base}/users")
    if res.status_code != 200:
        st.error("❌ 無法取得帳號資料")
        return
    users = res.json()

    # ✅ 搜尋欄位
    keyword = st.text_input("🔍 輸入使用者 ID 或帳號名稱查詢")

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
        st.warning("查無符合條件的使用者")
        return

    # ✅ 顯示 AgGrid 表格
    col1, col2 = st.columns([2.2, 1])
    with col1:
        st.subheader("📋 使用者清單")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection("single", use_checkbox=True)
        for col in ["使用者ID", "帳號名稱", "是否為管理員", "啟用狀態", "備註"]:
            gb.configure_column(col, editable=False)
        grid_response = AgGrid(
            df,
            gridOptions=gb.build(),
            update_mode="SELECTION_CHANGED",
            height=400,
            theme="streamlit"
        )

    # ✅ 操作選單區塊
    selected_rows = grid_response.get("selected_rows", [])
    if len(selected_rows) > 0:
        selected = selected_rows[0]
        user_id = selected["使用者ID"]
        username = selected["帳號名稱"]
        status = selected["啟用狀態"]

        with col2:
            st.subheader("🔧 帳號操作")
            st.write(f"🆔 ID：{user_id}")
            st.write(f"👤 帳號：{username}")
            st.write(f"🔒 狀態：{status}")

            # ✅ 操作選單
            if status == "啟用中":
                action = st.selectbox("請選擇操作", ["停用帳號", "刪除帳號", "修改密碼"])
            else:
                action = st.selectbox("請選擇操作", ["啟用帳號", "刪除帳號", "修改密碼"])

            # ✅ 修改密碼欄位
            if action == "修改密碼":
                new_pw = st.text_input("🔑 新密碼", type="password")
            else:
                new_pw = None

            # ✅ 執行操作
            if st.button("✅ 執行操作"):
                if action == "啟用帳號":
                    r = requests.post(f"{api_base}/enable_user/{user_id}")
                elif action == "停用帳號":
                    r = requests.post(f"{api_base}/disable_user/{user_id}")
                elif action == "刪除帳號":
                    r = requests.delete(f"{api_base}/delete_user/{user_id}")
                elif action == "修改密碼":
                    if not new_pw:
                        st.warning("請輸入新密碼")
                        return
                    r = requests.put(f"{api_base}/update_user_password/{user_id}", json={"new_password": new_pw})
                else:
                    r = None

                if r and r.status_code == 200:
                    st.success("✅ 操作成功，請重新整理頁面")
                else:
                    st.error(f"❌ 操作失敗：{r.text if r else '無回應'}")
