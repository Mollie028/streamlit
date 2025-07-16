import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

API_BASE_URL = "https://ocr-whisper-production-2.up.railway.app"

def run():
    st.set_page_config(page_title="帳號管理", page_icon="👤", layout="wide")

    st.markdown("""
        <style>
        .ag-theme-streamlit .ag-root-wrapper {
            height: 380px !important;
            width: 95% !important;
            margin: auto;
        }
        .ag-header-cell-label, .ag-cell {
            justify-content: center;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 👤 帳號清單")

    if "user_info" not in st.session_state:
        st.error("⚠️ 請先登入帳號")
        st.stop()

    current_user = st.session_state["user_info"]
    is_admin = current_user.get("is_admin", False)
    current_user_id = current_user.get("id")

    # 取得所有使用者
    @st.cache_data
    def get_users():
        try:
            res = requests.get(f"{API_BASE_URL}/users")
            if res.status_code == 200:
                return res.json()
            else:
                st.error("❌ 無法取得使用者資料。")
                return []
        except Exception as e:
            st.error("❌ 連線錯誤：" + str(e))
            return []

    users = get_users()
    if not users:
        st.stop()

    # 整理顯示資料
    records = []
    for user in users:
        uid = user.get("id")
        is_active = user.get("is_active", True)
        current_status = "啟用中" if is_active else "停用帳號"

        # 動態選項
        if current_status == "啟用中":
            options = ["停用帳號", "刪除帳號"]
        elif current_status == "停用帳號":
            options = ["啟用帳號", "刪除帳號"]
        else:
            options = ["刪除帳號"]  # 保底

        records.append({
            "使用者ID": uid,
            "帳號名稱": user.get("username"),
            "公司名稱": user.get("company_name", ""),
            "是否為管理員": bool(user.get("is_admin", False)),
            "狀態": current_status,
            "狀態選項": options,
            "備註": user.get("note", "")
        })

    df = pd.DataFrame(records)

    # AgGrid 設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)

    gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")

    # 🔽 狀態欄用 JS 抓狀態選項
    gb.configure_column(
        "狀態",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": {"function": "params.data['狀態選項']"}}
    )

    gb.configure_column("備註", editable=True)
    gb.configure_column("狀態選項", hide=True)  # ❌ 不顯示技術欄

    grid_return = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=380,
        theme="streamlit",
        allow_unsafe_jscode=True,
        return_mode="AS_INPUT"
    )

    selected_rows = grid_return["selected_rows"]

    # 儲存變更
    if st.button("💾 儲存變更"):
        if len(selected_rows) == 0:
            st.warning("⚠️ 請至少勾選一筆帳號")
        else:
            success_count = 0
            for row in selected_rows:
                user_id = row.get("使用者ID")
                if not (is_admin or user_id == current_user_id):
                    continue

                # 狀態操作
                status = row.get("狀態")
                if status == "啟用帳號":
                    requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
                elif status == "停用帳號":
                    requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
                elif status == "刪除帳號":
                    requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

                payload = {
                    "is_admin": row.get("是否為管理員", False),
                    "note": row.get("備註", "")
                }
                requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

                success_count += 1

            st.success(f"✅ 已成功儲存 {success_count} 筆帳號變更")

    # 返回首頁
    if st.button("🔙 返回主頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
