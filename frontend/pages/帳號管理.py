import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import requests

API_BASE = "https://ocr-whisper-production-2.up.railway.app"

# ---------------------- Functions ----------------------
def get_user_list():
    try:
        res = requests.get(f"{API_BASE}/users")
        return res.json()
    except Exception as e:
        st.error("取得使用者清單失敗")
        return []

def update_note(user_id, new_note):
    try:
        res = requests.put(f"{API_BASE}/users/{user_id}/note", json={"note": new_note})
        return res.status_code == 200
    except:
        return False

def enable_account(user_id):
    try:
        res = requests.put(f"{API_BASE}/users/{user_id}/enable")
        return res.status_code == 200
    except:
        return False

def update_role(user_id, is_admin):
    try:
        res = requests.put(f"{API_BASE}/users/{user_id}/role", json={"is_admin": is_admin})
        return res.status_code == 200
    except:
        return False

# ---------------------- Page Main ----------------------
def main():
    st.markdown("""
        <h2>👥 帳號管理</h2>
        <h4>所有使用者帳號（可互動）</h4>
    """, unsafe_allow_html=True)

    users = get_user_list()
    if not users:
        st.stop()

    df = pd.DataFrame(users)
    df.rename(columns={"id": "使用者編號", "username": "使用者帳號", "is_admin": "是否為管理員",
                        "company_name": "公司名稱", "note": "備註說明", "is_active": "帳號狀態"}, inplace=True)

    df["是否為管理員"] = df["是否為管理員"].apply(lambda x: "✅ 是" if x else "❌ 否")
    df["帳號狀態"] = df["帳號狀態"].apply(lambda x: "🟢 啟用中" if x else "⚫ 已停用")

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_column("備註說明", editable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        height=300,
        fit_columns_on_grid_load=True
    )

    updated_rows = grid_response["data"]
    if st.button("💾 儲存備註修改"):
        success_count = 0
        for i, row in updated_rows.iterrows():
            user_id = int(row["使用者編號"])
            note = row["備註說明"]
            if update_note(user_id, note):
                success_count += 1
        st.success(f"成功更新 {success_count} 筆備註")

    st.markdown("""---
    <h4>🔧 帳號操作區</h4>
    """, unsafe_allow_html=True)

    selected_id = st.number_input("請輸入要編輯的使用者 ID：", min_value=1, step=1)
    if selected_id:
        target_user = next((u for u in users if u["id"] == selected_id), None)
        if target_user:
            st.info(f"你正在編輯帳號：{target_user['username']}")

            if not target_user["is_active"]:
                if st.button("✅ 啟用此帳號"):
                    if enable_account(selected_id):
                        st.success("帳號已成功啟用")
                    else:
                        st.error("帳號啟用失敗")

            new_role = st.radio("變更使用者權限：", ["管理員", "一般使用者"],
                                index=0 if target_user["is_admin"] else 1)
            role_bool = True if new_role == "管理員" else False
            if st.button("✅ 確認修改權限"):
                if update_role(selected_id, role_bool):
                    st.success("使用者權限已更新")
                else:
                    st.error("修改權限失敗")
        else:
            st.warning("找不到對應使用者 ID")

def run():
    main()

if __name__ == "__main__":
    run()
