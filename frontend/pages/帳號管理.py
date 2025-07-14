import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------------
# API 設定
# -------------------------
API_URL = "https://ocr-whisper-production-2.up.railway.app"
GET_USERS_URL = f"{API_URL}/users"
UPDATE_USER_URL = f"{API_URL}/update_user"

# -------------------------
# 輔助函式
# -------------------------
def get_users():
    try:
        response = requests.get(GET_USERS_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"無法載入帳號資料：{e}")
    return []

def update_user(user_id, data):
    try:
        res = requests.put(f"{UPDATE_USER_URL}/{user_id}", json=data)
        return res.status_code == 200
    except Exception as e:
        st.error(f"更新失敗：{e}")
        return False

# -------------------------
# 畫面主程式
# -------------------------
def run():
    st.title("👨‍💼 帳號管理")
    st.subheader("所有使用者帳號（可互動）")

    users = get_users()

    if users:
        df_data = []
        for user in users:
            df_data.append({
                "使用者編號": user.get("id"),
                "使用者帳號": user.get("username"),
                "是否為管理員": "✅ 是" if user.get("is_admin", False) else "❌ 否",
                "公司名稱": user.get("company", ""),
                "備註說明": user.get("note", ""),
                "帳號狀態": "🟢 啟用中" if user.get("active", False) else "🔴 停用中"
            })

        df = pd.DataFrame(df_data)

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
        gb.configure_column("備註說明", editable=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            height=300,
            use_container_width=True,
            update_mode=GridUpdateMode.MANUAL,
        )

        updated_rows = grid_response["data"]
        modified_rows = grid_response.get("updated_rows", [])

        if st.button("✅ 儲存所有變更"):
            success_count = 0
            for index, row in updated_rows.iterrows():
                user_id = row["使用者編號"]
                is_admin = row["是否為管理員"] == "✅ 是"
                active = row["帳號狀態"] == "🟢 啟用中"
                note = row["備註說明"]
                update_data = {
                    "is_admin": is_admin,
                    "active": active,
                    "note": note
                }
                if update_user(user_id, update_data):
                    success_count += 1
            st.success(f"✅ 成功更新 {success_count} 筆使用者資料！")
    else:
        st.warning("無使用者資料可顯示。")
