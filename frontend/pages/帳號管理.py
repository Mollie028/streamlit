import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

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
# 主畫面邏輯
# -------------------------
def main():
    st.title("👨‍💼 帳號管理")
    st.subheader("所有使用者帳號（可互動編輯）")

    users = get_users()
    if not users:
        st.warning("無使用者資料可顯示。")
        return

    df = pd.DataFrame(users)
    df["是否為管理員"] = df["is_admin"].apply(lambda x: "✅ 是" if x else "❌ 否")
    df["帳號狀態"] = df.get("active", True).apply(lambda x: "🟢 啟用中" if x else "🔴 停用中")
    df["備註說明"] = df["note"].fillna("")

    display_df = df[["id", "username", "是否為管理員", "company", "note", "帳號狀態"]]
    display_df.columns = ["使用者編號", "使用者帳號", "是否為管理員", "公司名稱", "備註說明", "帳號狀態"]

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
    gb.configure_column("帳號狀態", editable=False)
    gb.configure_column("是否為管理員", editable=False)

    grid_options = gb.build()
    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode="MODEL_CHANGED",
        height=350,
        use_container_width=True,
        allow_unsafe_jscode=True
    )

    st.divider()
    st.markdown("### 🖋️ 編輯選擇的使用者資料")

    selected_rows = grid_response["selected_rows"]
    if selected_rows:
        row = selected_rows[0]
        user_id = row["使用者編號"]
        username = row["使用者帳號"]

        st.info(f"🧾 你正在編輯帳號：**{username}** (ID: {user_id})")

        new_note = st.text_input("備註說明：", value=row["備註說明"])
        new_password = st.text_input("新密碼（可留空跳過）", type="password")
        active = st.checkbox("✅ 啟用帳號", value=row["帳號狀態"] == "🟢 啟用中")

        if st.button("✅ 確認更新"):
            update_data = {
                "note": new_note,
                "active": active
            }
            if new_password:
                update_data["password"] = new_password
            success = update_user(user_id, update_data)
            if success:
                st.success("✅ 使用者資料更新成功，請重新整理！")
            else:
                st.error("❌ 更新失敗，請稍後再試。")

        if st.button("🗑️ 刪除帳號", type="primary"):
            confirm = st.checkbox("我確認要永久刪除此帳號！")
            if confirm:
                if delete_user(user_id):
                    st.success("✅ 使用者已刪除。請重新整理。")
                else:
                    st.error("❌ 刪除失敗。")

    else:
        st.caption("請點選上表中的任一列進行編輯")

# -------------------------
# 包裝給 app.py 呼叫
# -------------------------
def run():
    main()
