# frontend/pages/帳號管理.py
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import requests

# -------------------------
# API 設定
# -------------------------
API_URL = "https://ocr-whisper-production-2.up.railway.app"
GET_USERS_URL = f"{API_URL}/users"
UPDATE_USER_URL = f"{API_URL}/update_user"

# -------------------------
# 護助函式
# -------------------------
def get_users():
    try:
        res = requests.get(GET_USERS_URL)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"無法載入帳號資料: {e}")
    return []

def update_user(user_id, data):
    try:
        res = requests.put(f"{UPDATE_USER_URL}/{user_id}", json=data)
        return res.status_code == 200
    except Exception as e:
        st.error(f"更新失敗: {e}")
        return False

# -------------------------
# 主程式
# -------------------------
def main():
    st.title("🧑‍💼 帳號管理")
    st.subheader("所有使用者帳號（可互動）")

    users = get_users()

    if users:
        df_data = []
        for user in users:
            df_data.append({
                "使用者編號": user["id"],
                "使用者帳號": user["username"],
                "是否為管理員": "✅ 是" if user["is_admin"] else "❌ 否",
                "公司名稱": user.get("company", ""),
                "備註說明": user.get("note", ""),
                "帳號狀態": "🟢 啟用中" if user.get("active", True) else "🔴 停用中"
            })

        df = pd.DataFrame(df_data)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
        grid_options = gb.build()
        AgGrid(df, gridOptions=grid_options, height=250)

        st.divider()
        st.markdown("### ✏️ 帳號操作區")
        keyword = st.text_input("請輸入要編輯的使用者 ID 或帳號名稱:")

        selected_user = None
        for u in users:
            if keyword and (str(u["id"]) == keyword or u["username"] == keyword):
                selected_user = u
                break

        if selected_user:
            st.info(f"你正在編輯帳號：**{selected_user['username']}**")

            role = st.radio("變更使用者權限:", ["管理員", "一般使用者"],
                             index=0 if selected_user["is_admin"] else 1)

            is_active = st.checkbox("帳號啟用", value=selected_user.get("active", True))
            new_password = st.text_input("🔐 請輸入新密碼（可空白跳過）:", type="password")
            new_note = st.text_input("備註說明：", value=selected_user.get("note") or "")

            if st.button("✅ 確認更新使用者資料"):
                update_data = {
                    "is_admin": role == "管理員",
                    "active": is_active,
                    "note": new_note
                }
                if new_password:
                    update_data["password"] = new_password

                success = update_user(selected_user["id"], update_data)
                if success:
                    st.success("✅ 使用者資料更新成功！請重新整理以查看變更。")
                else:
                    st.error("❌ 更新失敗，請稍後再試。")
        elif keyword:
            st.warning("查無符合的帳號，請確認輸入是否正確。")
    else:
        st.warning("無使用者資料可顯示。")

# -------------------------
# run() 函式
# -------------------------
def run():
    main()
