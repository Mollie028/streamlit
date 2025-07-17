import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

API_URL = "https://ocr-whisper-production-2.up.railway.app"

st.set_page_config(page_title="帳號清單", page_icon="🧑🏻‍💻", layout="wide")
st.title("🧑🏻‍💻 帳號清單")

# 取得所有使用者資料
try:
    response = requests.get(f"{API_URL}/users")
    users = response.json()
    if isinstance(users, dict) and "detail" in users:
        st.warning("尚無有效使用者資料，請稍後再試。")
        st.stop()
except Exception as e:
    st.error("❌ 無法取得使用者資料，請確認後端 API 是否正常。")
    st.stop()

# 確保每筆資料都有完整欄位
for user in users:
    user.setdefault("status", "啟用中" if user.get("is_active", True) else "停用帳號")
    user.setdefault("company", "未指定")
    user.setdefault("note", "")

# 建立欄位顯示名稱對照表
column_name_map = {
    "id": "使用者ID",
    "username": "帳號名稱",
    "is_admin": "是否為管理員",
    "company": "公司名稱",
    "is_active": "啟用中",
    "note": "備註",
    "status": "狀態",
}

# 建立 AgGrid 欄位設定
gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(users))

# 中文欄位順序
display_columns = ["id", "username", "is_admin", "company", "is_active", "note", "status"]
gb.configure_default_column(editable=False, resizable=True)

gb.configure_column("id", header_name=column_name_map["id"], editable=False, width=90)
gb.configure_column("username", header_name=column_name_map["username"], editable=False)
gb.configure_column("is_admin", header_name=column_name_map["is_admin"], editable=False, cellRenderer="checkboxRenderer")
gb.configure_column("company", header_name=column_name_map["company"], editable=True)
gb.configure_column("is_active", header_name=column_name_map["is_active"], editable=False, cellRenderer="checkboxRenderer")
gb.configure_column("note", header_name=column_name_map["note"], editable=True)

# 狀態欄位改為下拉選單
status_options = ["啟用中", "停用帳號", "刪除帳號"]
gb.configure_column(
    "status",
    header_name=column_name_map["status"],
    editable=True,
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": status_options},
)

# 顯示 AgGrid 表格
grid_response = AgGrid(
    pd.DataFrame(users)[display_columns],
    gridOptions=gb.build(),
    height=380,
    fit_columns_on_grid_load=True,
    update_mode=GridUpdateMode.MANUAL,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
)

# 處理修改後資料
updated_rows = grid_response["data"]

# 儲存變更按鈕
if st.button("💾 儲存變更"):
    success_count = 0
    for row in updated_rows.itertuples(index=False):
        user_id = row.id
        payload = {
            "company": row.company,
            "note": row.note
        }
        try:
            # 更新基本資料
            requests.put(f"{API_URL}/update_user/{user_id}", json=payload)

            # 更新狀態
            if row.status == "啟用中":
                requests.put(f"{API_URL}/enable_user/{user_id}")
            elif row.status == "停用帳號":
                requests.put(f"{API_URL}/disable_user/{user_id}")
            elif row.status == "刪除帳號":
                requests.delete(f"{API_URL}/delete_user/{user_id}")
            success_count += 1
        except Exception:
            pass

    st.success(f"✅ 已成功儲存 {success_count} 筆資料。")
    st.experimental_rerun()

# 返回主頁
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")
