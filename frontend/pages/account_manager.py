import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from core.config import API_BASE

def run():
    # 登入檢查
    if "access_token" not in st.session_state or "user" not in st.session_state:
        st.warning("⚠️ 尚未登入，請先登入帳號")
        st.stop()

    token = st.session_state["access_token"]
    current_user = st.session_state["user"]
    is_admin = current_user.get("role") == "admin"

    st.title("👥 帳號管理")

    # 取得使用者清單
    try:
        res = requests.get(f"{API_BASE}/users", headers={"Authorization": f"Bearer {token}"})
        users = res.json()
    except Exception as e:
        st.error("無法取得帳號資料")
        st.stop()

    df = pd.DataFrame(users)
    if df.empty:
        st.info("目前沒有任何使用者帳號")
        return

    df = df[["id", "username", "is_admin", "is_active", "note"]]
    df.columns = ["ID", "使用者帳號", "是否為管理員", "使用者狀況", "備註"]
    df.reset_index(drop=True, inplace=True)
    df["是否為管理員"] = df["是否為管理員"].astype(bool)
    df["使用者狀況"] = df["使用者狀況"].map({True: "啟用", False: "停用"})

    # 建立表格設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("是否為管理員", editable=is_admin, cellEditor='agSelectCellEditor', cellEditorParams={'values': [True, False]})
    gb.configure_column("使用者狀況", editable=is_admin, cellEditor='agSelectCellEditor', cellEditorParams={'values': ["啟用", "停用", "刪除"]})
    gb.configure_column("備註", editable=is_admin)

    gb.configure_grid_options(
        domLayout='normal',
        pagination=True,
        paginationPageSize=5,
        singleClickEdit=True  # ✅ 只需單擊即可編輯
    )
    grid_options = gb.build()

    st.markdown("### 使用者帳號列表")
    grid = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        height=380,
        fit_columns_on_grid_load=True
    )

    updated_df = grid["data"]

if st.button("💾 儲存變更"):
    token = st.session_state.get("access_token", "")
    success_count = 0

    for _, row in updated_df.iterrows():
        if not is_admin:
            continue

        # 根據 ID 找原始資料
        original = df[df["ID"] == row["ID"]].iloc[0]
        user_id = row["ID"]
        changed = False

        # 比對狀態（啟用／停用／刪除）
        if row["使用者狀況"] != original["使用者狀況"]:
            status = row["使用者狀況"]
            if status == "啟用":
                requests.put(f"{API_BASE}/enable_user/{user_id}", headers={"Authorization": f"Bearer {token}"})
            elif status == "停用":
                requests.put(f"{API_BASE}/disable_user/{user_id}", headers={"Authorization": f"Bearer {token}"})
            elif status == "刪除":
                requests.delete(f"{API_BASE}/delete_user/{user_id}", headers={"Authorization": f"Bearer {token}"})
                continue  # 刪除就不用送更新資料
            changed = True

        # 比對管理員權限與備註欄位
        update_payload = {}
        if row["是否為管理員"] != original["是否為管理員"]:
            update_payload["is_admin"] = row["是否為管理員"]
            changed = True
        if row["備註"] != original["備註"]:
            update_payload["note"] = row["備註"]
            changed = True

        # 若有需更新欄位，就送出
        if update_payload:
            res = requests.put(f"{API_BASE}/update_user/{user_id}", json=update_payload, headers={"Authorization": f"Bearer {token}"})
            if res.status_code != 200:
                st.error(f"❌ 更新失敗：{row['使用者帳號']}")
            else:
                success_count += 1

    st.success(f"✅ 成功儲存 {success_count} 筆變更！")
    st.rerun()



    # 底部功能列：返回主頁／登出
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 返回主頁"):
            st.session_state["current_page"] = "home"
            st.rerun()
    with col2:
        if st.button("🚪 登出"):
            st.session_state.clear()
            st.rerun()
