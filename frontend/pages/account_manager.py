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
        for i, row in updated_df.iterrows():
            original = df.iloc[i]
            if not is_admin:
                continue

            if row.to_dict() != original.to_dict():
                user_id = row["ID"]
                new_data = {
                    "is_admin": row["是否為管理員"],
                    "note": row["備註"],
                }

                if row["使用者狀況"] != original["使用者狀況"]:
                    if row["使用者狀況"] == "啟用":
                        requests.put(f"{API_BASE}/enable_user/{user_id}", headers={"Authorization": f"Bearer {token}"})
                    elif row["使用者狀況"] == "停用":
                        requests.put(f"{API_BASE}/disable_user/{user_id}", headers={"Authorization": f"Bearer {token}"})
                    elif row["使用者狀況"] == "刪除":
                        requests.delete(f"{API_BASE}/delete_user/{user_id}", headers={"Authorization": f"Bearer {token}"})
                        continue

                res = requests.put(f"{API_BASE}/update_user/{user_id}", json=new_data, headers={"Authorization": f"Bearer {token}"})
                if res.status_code != 200:
                    st.error(f"更新失敗：{row['使用者帳號']}")

        st.success("✅ 變更已儲存")
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
