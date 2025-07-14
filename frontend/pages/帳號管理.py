import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# -------------------------
# API 設定
# -------------------------
API_URL = "https://ocr-whisper-production-2.up.railway.app"
GET_USERS_URL = f"{API_URL}/users"
UPDATE_USER_URL = f"{API_URL}/update_user"
DELETE_USER_URL = f"{API_URL}/delete_user"

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

def delete_user(user_id):
    try:
        res = requests.delete(f"{DELETE_USER_URL}/{user_id}")
        return res.status_code == 200
    except Exception as e:
        st.error(f"刪除失敗：{e}")
        return False

# -------------------------
# 畫面
# -------------------------
st.title("👨\u200d💼 帳號管理")
st.subheader("所有使用者帳號（可編輯、刪除）")

users = get_users()

if users:
    df_data = []
    for user in users:
        df_data.append({
            "使用者編號": user.get("id"),
            "使用者帳號": user.get("username"),
            "是否為管理員": user.get("is_admin", False),
            "公司名稱": user.get("company", ""),
            "備註說明": user.get("note", ""),
            "帳號狀態": user.get("active", False),
        })

    df = pd.DataFrame(df_data)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_grid_options(domLayout='normal')
    gb.configure_column("使用者帳號", editable=False)
    gb.configure_column("使用者編號", editable=False)
    gb.configure_column("帳號狀態", cellEditor="agSelectCellEditor", cellEditorParams={"values": [True, False]})
    gb.configure_column("是否為管理員", cellEditor="agSelectCellEditor", cellEditorParams={"values": [True, False]})

    grid_options = gb.build()

    grid_return = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        fit_columns_on_grid_load=True,
        use_container_width=True,
        height=400,
    )

    edited_rows = grid_return["data"]

    st.markdown("---")
    st.markdown("### 🔐 修改密碼 / 🗑️ 刪除帳號")
    selected_id = st.text_input("請輸入欲修改或刪除的使用者 ID：")

    if selected_id:
        user = next((u for u in users if str(u.get("id")) == selected_id), None)
        if user:
            st.info(f"目前選擇帳號：{user['username']}")

            with st.expander("🔐 修改密碼"):
                new_pass = st.text_input("請輸入新密碼", type="password")
                if st.button("✅ 確認修改密碼"):
                    if new_pass:
                        success = update_user(user["id"], {"password": new_pass})
                        if success:
                            st.success("密碼更新成功！")
                        else:
                            st.error("密碼更新失敗。")

            with st.expander("🗑️ 刪除帳號"):
                if st.button("⚠️ 確認刪除帳號"):
                    confirm = st.checkbox("我確認要刪除此帳號")
                    if confirm:
                        success = delete_user(user["id"])
                        if success:
                            st.success("帳號已刪除，請重新整理頁面")
                        else:
                            st.error("刪除失敗。")
        else:
            st.warning("查無使用者，請確認 ID 是否正確")

    st.markdown("---")
    if st.button("💾 儲存上方表格變更"):
        updated_count = 0
        for _, row in edited_rows.iterrows():
            uid = row["使用者編號"]
            payload = {
                "is_admin": row["是否為管理員"],
                "note": row["備註說明"],
                "active": row["帳號狀態"]
            }
            if update_user(uid, payload):
                updated_count += 1
        st.success(f"✅ 已更新 {updated_count} 筆使用者資料")
else:
    st.warning("無使用者資料可顯示。")
