import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder

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
        res = requests.get(GET_USERS_URL)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"❌ 載入使用者失敗，狀態碼：{res.status_code}")
    except Exception as e:
        st.error(f"❌ 無法載入帳號資料：{e}")
    return []

def update_user(user_id, data):
    try:
        res = requests.put(f"{UPDATE_USER_URL}/{user_id}", json=data)
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 更新失敗：{e}")
        return False

def delete_user(user_id):
    try:
        res = requests.delete(f"{DELETE_USER_URL}/{user_id}")
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 刪除失敗：{e}")
        return False

# -------------------------
# 主畫面邏輯
# -------------------------
def main():
    st.title("👨‍💼 帳號管理")
    st.subheader("所有使用者帳號（可互動編輯）")

    users = get_users()
    if not users or not isinstance(users, list):
        st.warning("⚠️ 無使用者資料可顯示。")
        return

    df = pd.DataFrame(users)

    # 欄位安全檢查
    for col in ["id", "username", "is_admin", "is_active", "note", "company"]:
        if col not in df.columns:
            df[col] = ""

    # 顯示用欄位轉換
    df["是否為管理員"] = df["is_admin"].apply(lambda x: "✅ 是" if x else "❌ 否")
    df["帳號狀態"] = df["is_active"].apply(lambda x: "🟢 啟用中" if x else "🔴 停用中")
    df["備註說明"] = df["note"].fillna("")
    df["公司名稱"] = df["company"].fillna("")

    display_df = df[["id", "username", "是否為管理員", "公司名稱", "備註說明", "帳號狀態"]]
    display_df.columns = ["使用者編號", "使用者帳號", "是否為管理員", "公司名稱", "備註說明", "帳號狀態"]

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_selection("single")
    gb.configure_column("帳號狀態", editable=False)
    gb.configure_column("是否為管理員", editable=False)
    gb.configure_column("使用者帳號", editable=False)

    grid_response = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode="MODEL_CHANGED",
        allow_unsafe_jscode=True,
        height=400,
        use_container_width=True
    )

    st.divider()
    st.markdown("### 🖋️ 編輯選擇的使用者資料")

    selected = grid_response["selected_rows"]
    if selected:
        row = selected[0]
        user_id = row["使用者編號"]
        username = row["使用者帳號"]

        st.info(f"🧾 你正在編輯帳號：**{username}** (ID: {user_id})")

        new_note = st.text_input("備註說明：", value=row["備註說明"])
        new_password = st.text_input("新密碼（可留空略過）", type="password")
        is_active = st.checkbox("✅ 啟用帳號", value=row["帳號狀態"] == "🟢 啟用中")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 確認更新"):
                update_data = {"note": new_note, "active": is_active}
                if new_password:
                    update_data["password"] = new_password
                if update_user(user_id, update_data):
                    st.success("✅ 使用者更新成功，請重新整理。")
                else:
                    st.error("❌ 更新失敗。")

        with col2:
            if st.button("🗑️ 刪除帳號"):
                confirm = st.checkbox("我確認要永久刪除此帳號")
                if confirm:
                    if delete_user(user_id):
                        st.success("✅ 使用者已刪除。請重新整理。")
                    else:
                        st.error("❌ 刪除失敗。")
    else:
        st.caption("📌 請先在上方表格中選取一筆帳號進行操作")

# -------------------------
# 包裝給 app.py 呼叫
# -------------------------
def run():
    main()
