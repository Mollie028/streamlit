import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from core.config import API_BASE

# ✅ 手動寫一個 go_home_button（避免匯入錯誤）
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
            data = res.json()
        else:
            st.error("🚫 無法取得使用者清單")
            return
    except Exception as e:
        st.error("❌ 錯誤")
        st.code(str(e))
        return

    df = pd.DataFrame(data)
    if df.empty:
        st.info("目前沒有帳號資料")
        return

    # ✅ 欄位轉換（避免缺欄位錯誤）
    rename_map = {
        "id": "ID",
        "username": "帳號",
        "company_name": "公司",
        "note": "備註",
        "is_active": "啟用中"
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ✅ 權限欄位處理（穩定寫法）
    if "role" in df.columns:
        df["權限"] = df["role"].map({"admin": "管理員", "user": "使用者"})
    else:
        st.warning("⚠️ 缺少 role 欄位，請確認後端 /users API 是否正確")
        return

    if "啟用中" in df.columns:
        df["啟用中"] = df["啟用中"].map({True: "啟用", False: "停用"})

    # ✅ AgGrid 設定
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
        height=500,
        theme="streamlit"
    )

    updated_rows = grid["data"]
    selected_rows = grid["selected_rows"]

    # ✅ 儲存按鈕
    if st.button("💾 儲存變更"):
        # ✅ 改為根據「修改欄位差異」自動檢查，而非靠選取
        if not updated_rows:
            st.warning("⚠️ 沒有任何變更資料")
            return

        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

        success_count = 0
        for row in updated_rows:
            user_id = row.get("ID")
            if not user_id:
                continue

            payload = {
                "username": row.get("帳號", ""),
                "company_name": row.get("公司", ""),
                "note": row.get("備註", ""),
                "is_active": row.get("啟用中") == "啟用",
                "role": "admin" if row.get("權限") == "管理員" else "user"
            }

            try:
                res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload, headers=headers)
                if res.status_code == 200:
                    success_count += 1
                else:
                    st.warning(f"❗ 帳號 {row.get('帳號')} 更新失敗：{res.text}")
            except Exception as e:
                st.error(f"❌ 帳號 {row.get('帳號')} 發生錯誤")
                st.code(str(e))

        st.success(f"✅ 成功儲存 {success_count} 筆變更")
        st.rerun()
