import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.stylable_container import stylable_container

API_BASE = "https://ocr-whisper-production-2.up.railway.app"

def run():
    st.title("🛠️ 帳號管理頁")

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    res = requests.get(f"{API_BASE}/users", headers=headers)
    data = res.json()

    if not isinstance(data, list):
        st.error("❌ 取得使用者資料失敗")
        return

    df = pd.DataFrame(data)

    if df.empty:
        st.info("目前沒有帳號資料")
        return

    # 欄位映射
    df["啟用中"] = df["is_active"].map({True: "啟用", False: "停用"})
    df["權限"] = df["role"].map({"admin": "管理員", "user": "使用者"})
    df.rename(columns={"id": "ID", "username": "帳號", "company_name": "公司", "note": "備註"}, inplace=True)

    # 檢查是否有 ID 重複
    duplicate_ids = df["ID"][df["ID"].duplicated()].unique()
    if len(duplicate_ids) > 0:
        st.warning(f"⚠️ 偵測到重複 ID：{', '.join(map(str, duplicate_ids))}，系統將使用帳號 (username) 作為唯一識別。")

    st.subheader("🔧 批次操作（先勾選帳號）")
    batch_status = st.selectbox("批次變更啟用狀態", ["-- 不變更 --", "啟用", "停用"])
    batch_role = st.selectbox("批次變更權限", ["-- 不變更 --", "管理員", "使用者"])

    st.subheader("📋 使用者清單（可編輯）")

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_column("帳號", header_name="帳號", editable=False)
    gb.configure_column("ID", editable=False, hide=True)
    gb.configure_column("is_admin", hide=True)
    gb.configure_column("is_active", hide=True)
    gb.configure_column("role", hide=True)
    gb.configure_column("公司", editable=True)
    gb.configure_column("啟用中", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用", "停用"]})
    gb.configure_column("權限", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": ["管理員", "使用者"]})
    gb.configure_column("備註", editable=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        height=380,
        width="100%",
        theme="balham",
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True
    )

    selected_rows = grid_response["selected_rows"]

    st.divider()
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("💾 儲存變更", use_container_width=True):
            if not selected_rows:
                st.warning("⚠️ 請至少選取一筆帳號資料")
            else:
                success = True
                username_to_id = dict(zip(df["帳號"], df["ID"]))

                for row in selected_rows:
                    username = row.get("帳號")
                    user_id = username_to_id.get(username)
                    if not user_id:
                        st.warning(f"❗ 找不到帳號 {username} 對應的 ID，略過")
                        continue

                    try:
                        if batch_status != "-- 不變更 --":
                            row["啟用中"] = batch_status
                        if batch_role != "-- 不變更 --":
                            row["權限"] = batch_role

                        payload = {
                            "username": username,
                            "company_name": row.get("公司", ""),
                            "note": row.get("備註", ""),
                            "is_active": row.get("啟用中") == "啟用",
                            "role": "admin" if row.get("權限") == "管理員" else "user"
                        }

                        res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload, headers=headers)
                        if res.status_code != 200:
                            st.warning(f"❗ 帳號 {username} 更新失敗：{res.text}")
                            success = False
                    except Exception as e:
                        st.error(f"❌ 帳號 {username} 發生錯誤")
                        st.code(str(e))
                        success = False

                if success:
                    st.success("✅ 所有變更已儲存")
                    st.rerun()

    with col2:
        st.info("⬅ 請選擇要編輯的帳號，再按下左側按鈕儲存變更")

    st.markdown("### 🏠 [返回主頁](./)")
