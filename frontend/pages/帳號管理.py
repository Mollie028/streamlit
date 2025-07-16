import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

API_BASE_URL = "https://ocr-whisper-production-2.up.railway.app"

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

# 檢查登入者資訊
if "user_info" not in st.session_state:
    st.error("⚠️ 請先登入帳號")
    st.stop()

current_user = st.session_state["user_info"]
is_admin = current_user.get("is_admin", False)
current_user_id = current_user.get("id")

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

# 取得資料
users = get_users()
if not users:
    st.stop()

# 前處理（加上中文欄位）
processed = []
for user in users:
    uid = user.get("id")
    editable = is_admin or uid == current_user_id
    processed.append({
        "使用者ID": uid,
        "帳號名稱": user.get("username"),
        "公司名稱": user.get("company_name", ""),
        "是否為管理員": bool(user.get("is_admin", False)),
        "狀態": "啟用中" if user.get("is_active") else "停用帳號",
        "備註": user.get("note", ""),
        "新密碼": "",
        "可編輯": editable
    })

df_display = pd.DataFrame(processed)[["使用者ID", "帳號名稱", "公司名稱", "是否為管理員", "狀態", "備註", "新密碼"]]

# AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df_display)
gb.configure_selection("multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)

editable_fields = ["是否為管理員", "狀態", "備註", "新密碼"]
for col in editable_fields:
    gb.configure_column(col, editable=True)
gb.configure_column("是否為管理員", cellEditor="agCheckboxCellEditor")
gb.configure_column("狀態", cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": ["啟用中", "停用帳號", "啟用帳號", "刪除帳號"]})

grid_return = AgGrid(
    df_display,
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
    if not selected_rows:
        st.warning("⚠️ 請至少勾選一筆帳號")
    else:
        for row in selected_rows:
            user_id = row.get("使用者ID")
            if not (is_admin or user_id == current_user_id):
                continue  # 無權限編輯他人

            # 狀態處理
            status = row.get("狀態")
            if status == "啟用帳號":
                requests.put(f"{API_BASE_URL}/enable_user/{user_id}")
            elif status == "停用帳號":
                requests.put(f"{API_BASE_URL}/disable_user/{user_id}")
            elif status == "刪除帳號":
                requests.delete(f"{API_BASE_URL}/delete_user/{user_id}")

            # 內容更新
            payload = {
                "is_admin": row.get("是否為管理員", False),
                "note": row.get("備註", "")
            }
            requests.put(f"{API_BASE_URL}/update_user/{user_id}", json=payload)

            # 密碼更新
            new_password = row.get("新密碼", "").strip()
            if new_password:
                requests.put(f"{API_BASE_URL}/update_user_password/{user_id}", json={"password": new_password})

        st.success("✅ 變更已完成，請重新整理查看最新結果")

# 返回按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")  # ⬅️ 改成你的主頁路徑即可
