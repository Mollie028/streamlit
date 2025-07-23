import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from utils.auth import is_logged_in, logout_button
from core.config import API_BASE

def run():
    st.title("👥 帳號管理")

    # 登入驗證（選用）
    if not is_logged_in():
        st.warning("請先登入")
        return

    logout_button()

    # 取得帳號清單
    try:
        res = requests.get(f"{API_BASE}/users")
        if res.status_code == 200:
            users = res.json()
        else:
            st.error("❌ 無法載入帳號清單")
            return
    except Exception as e:
        st.error("❌ 載入失敗")
        st.code(str(e))
        return

    # AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(
        pd.DataFrame(users)[["id", "username", "is_admin", "is_active", "note"]]
    )
    gb.configure_default_column(editable=True)
    gb.configure_column("is_active", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用", "停用", "刪除"]})
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    st.markdown("### 使用者列表")
    grid_response = AgGrid(
        pd.DataFrame(users),
        gridOptions=grid_options,
        height=380,
        width='100%',
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        reload_data=True
    )

    edited_rows = grid_response["data"]

    # 儲存變更按鈕
    if st.button("💾 儲存變更"):
        st.toast("📡 更新帳號中...")
        try:
            for row in edited_rows:
                user_id = row["id"]
                payload = {
                    "note": row.get("note", ""),
                    "is_admin": row.get("is_admin", False),
                    "is_active": row.get("is_active", True),
                }
                res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload)
            st.success("✅ 資料更新成功")
        except Exception as e:
            st.error("❌ 更新失敗")
            st.code(str(e))
