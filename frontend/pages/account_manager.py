import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import requests
import pandas as pd

API_URL = "https://ocr-whisper-production-2.up.railway.app"

def run():
    st.title("👤 帳號管理")

    # ✅ 檢查登入狀態
    if "username" not in st.session_state or "user_id" not in st.session_state:
        st.error("⚠️ 請先登入")
        return

    login_username = st.session_state["username"]
    login_userid = st.session_state["user_id"]
    is_admin = st.session_state.get("is_admin", False)

    # ✅ 取得使用者列表
    res = requests.get(f"{API_URL}/users")
    if res.status_code != 200:
        st.error("❌ 無法取得使用者資料")
        return
    users = res.json()

    if not users:
        st.warning("⚠️ 尚無帳號資料")
        return

    # ✅ 整理為 DataFrame
    df = pd.DataFrame([{
        "使用者ID": u["id"],
        "帳號名稱": u["username"],
        "是否為管理員": u["is_admin"],
        "啟用狀態": "啟用中" if u["is_active"] else "已停用",
        "備註": u.get("note", "")
    } for u in users])

    st.subheader("📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(df)

    # ✅ 欄位設定
    gb.configure_column("使用者ID", editable=False)
    gb.configure_column("帳號名稱", editable=False)
    gb.configure_column("是否為管理員", editable=is_admin, cellEditor="agSelectCellEditor", cellEditorParams={"values": [True, False]})
    gb.configure_column("啟用狀態", editable=is_admin, cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用中", "已停用"]})
    gb.configure_column("備註", editable=is_admin)

    gb.configure_selection("multiple", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        fit_columns_on_grid_load=True,
        height=450,
        theme="streamlit"
    )

    updated_df = grid_response["data"]
    selected = grid_response["selected_rows"]

    # ✅ 儲存變更按鈕
    if is_admin:
        st.markdown("### 💾 批次儲存修改")
        if st.button("✅ 儲存變更"):
            success = True
            for row in selected:
                uid = row["使用者ID"]
                # 限制非管理員不能編輯他人帳號
                if not is_admin and uid != login_userid:
                    st.warning(f"⛔ 無權限修改使用者 ID：{uid}")
                    continue

                # 找出修改後的資料列
                new_row = updated_df[updated_df["使用者ID"] == uid].iloc[0]
                payload = {
                    "is_admin": new_row["是否為管理員"],
                    "is_active": True if new_row["啟用狀態"] == "啟用中" else False,
                    "note": new_row["備註"]
                }
                r = requests.put(f"{API_URL}/update_user/{uid}", json=payload)
                if r.status_code != 200:
                    st.error(f"❌ 更新失敗（ID {uid}）：{r.text}")
                    success = False
            if success:
                st.success("✅ 所有變更已成功儲存，請重新整理頁面")

    else:
        st.info("🔒 一般使用者僅能檢視，無法進行編輯")
