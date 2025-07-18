import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from core.config import API_BASE

# ✅ 手動 go_home_button
def go_home_button():
    st.markdown(
        """
        <div style='text-align: right; margin-bottom: 10px;'>
            <a href="/" style='text-decoration: none;'>
                <button style='padding: 6px 16px; font-size: 14px;'>🏠 返回主頁</button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ✅ 僅限管理員
if "access_token" not in st.session_state or st.session_state.get("role") != "admin":
    st.error("⚠️ 請先登入管理員帳號")
    st.stop()

def run():
    st.set_page_config(page_title="帳號管理", layout="wide")
    st.title("👤 帳號管理")
    go_home_button()

    # ✅ 抓取使用者清單
    try:
        res = requests.get(f"{API_BASE}/users", headers={
            "Authorization": f"Bearer {st.session_state['access_token']}"
        })
        if res.status_code == 200:
            users = res.json()
        else:
            st.error("🚫 無法取得使用者清單")
            st.stop()
    except Exception as e:
        st.error("❌ 錯誤")
        st.code(str(e))
        st.stop()

    # ✅ 建立 DataFrame
    df = pd.DataFrame(users)
    if df.empty:
        st.warning("⚠️ 尚無使用者資料")
        st.stop()

    rename_map = {
        "id": "ID",
        "username": "帳號",
        "company_name": "公司",
        "note": "備註",
        "is_active": "啟用中",
        "role": "權限"
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    if "啟用中" in df.columns:
        df["啟用中"] = df["啟用中"].map({True: "啟用", False: "停用"})

    if "權限" in df.columns:
        df["權限"] = df["權限"].map({"admin": "管理員", "user": "使用者"})

    # ✅ 批次操作選單
    st.markdown("### 🔧 批次操作（先勾選帳號）")
    col1, col2 = st.columns(2)
    with col1:
        batch_status = st.selectbox("批次變更啟用狀態", ["-- 不變更 --", "啟用", "停用"])
    with col2:
        batch_role = st.selectbox("批次變更權限", ["-- 不變更 --", "管理員", "使用者"])

    # ✅ AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=True, wrapText=True, autoHeight=True, resizable=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_column("ID", editable=False)
    if "啟用中" in df.columns:
        gb.configure_column("啟用中", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用", "停用"]})
    if "權限" in df.columns:
        gb.configure_column("權限", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["管理員", "使用者"]})
    grid_options = gb.build()

    st.markdown("### 👇 使用者清單（可編輯）")
    grid = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        fit_columns_on_grid_load=True,
        height=400,
        theme="streamlit"
    )

    updated_df = grid["data"]
    selected_rows = grid["selected_rows"]

    # ✅ 儲存按鈕
    if st.button("💾 儲存變更"):
        if not selected_rows:
            st.warning("⚠️ 請至少選取一筆帳號資料")
            st.stop()

        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

        for row in selected_rows:
            user_id = row["ID"]
            try:
                # ✅ 套用批次操作設定（如果有）
                if batch_status != "-- 不變更 --":
                    row["啟用中"] = batch_status
                if batch_role != "-- 不變更 --":
                    row["權限"] = batch_role

                payload = {
                    "username": row.get("帳號", ""),
                    "company_name": row.get("公司", ""),
                    "note": row.get("備註", ""),
                    "is_active": row.get("啟用中") == "啟用",
                    "role": "admin" if row.get("權限") == "管理員" else "user"
                }

                res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload, headers=headers)
                if res.status_code != 200:
                    st.warning(f"❗ 帳號 {row['帳號']} 更新失敗：{res.text}")
            except Exception as e:
                st.error(f"❌ 帳號 {row.get('帳號')} 發生錯誤")
                st.code(str(e))

        st.success("✅ 所有變更已儲存")
        st.rerun()
