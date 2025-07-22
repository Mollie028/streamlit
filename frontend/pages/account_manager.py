import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import requests
from services.auth_service import is_logged_in, logout_button
from core.config import API_BASE


# 權限檢查
user_info = is_logged_in()
if not user_info:
    st.stop()
if not user_info.get("is_admin"):
    st.error("您沒有權限觀看此頁面。")
    st.stop()

st.markdown("## 🧑‍💼 使用者帳號清單")
st.markdown("以下為所有使用者帳號資料，僅限管理員修改")

# 返回主頁按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")

# 登出鍵（只保留一個）
logout_button()

# 從後端取得所有使用者資料
response = requests.get("https://ocr-whisper-production-2.up.railway.app/users")
if response.status_code != 200:
    st.error("無法取得使用者資料")
    st.stop()

users = response.json()
for user in users:
    user["使用者狀況"] = "啟用" if user["is_active"] else "停用"
    user["是否為管理員"] = user["is_admin"]
    user["使用者帳號"] = user["username"]

# 建立 AgGrid 設定
options = GridOptionsBuilder.from_dataframe(
    pd.DataFrame(users)[["id", "使用者帳號", "是否為管理員", "使用者狀況", "note"]]
)
options.configure_default_column(editable=True, resizable=True)
options.configure_column("id", header_name="ID", editable=False, pinned="left", width=80)
options.configure_column("使用者帳號", editable=False, pinned="left", width=200)
options.configure_column("是否為管理員", cellEditor="agCheckboxCellEditor", width=130)

# 使用者狀況下拉選單
status_options = ["啟用", "停用", "刪除"]
cellEditorParams = {"values": status_options, "cellRenderer": "agSelectCellEditor"}
options.configure_column("使用者狀況", cellEditor="agSelectCellEditor", cellEditorParams=cellEditorParams, width=120)

options.configure_column("note", header_name="備註", width=200)
options.configure_grid_options(domLayout='normal')
options.configure_grid_options(suppressCellFocus=False)
options.configure_grid_options(rowSelection='multiple')
options.configure_grid_options(suppressRowClickSelection=False)
options.configure_grid_options(alwaysShowHorizontalScroll=True)
options.configure_grid_options(suppressMovableColumns=True)
options.configure_grid_options(pagination=True, paginationPageSize=5)

# 加入只點一下就展開下拉選單的 JS (修正手機操作問題)
single_click_edit = JsCode('''
    class CustomCellEditor {
        init(params) {
            this.eInput = document.createElement('select');
            const options = ['啟用', '停用', '刪除'];
            options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.text = opt;
                this.eInput.appendChild(option);
            });
            this.eInput.value = params.value;
            this.eInput.style.width = '100%';
        }
        getGui() {
            return this.eInput;
        }
        afterGuiAttached() {
            this.eInput.focus();
        }
        getValue() {
            return this.eInput.value;
        }
        destroy() {}
        isPopup() {
            return false;
        }
    }
''')
options.configure_column("使用者狀況", cellEditorJsCode=single_click_edit, width=120)


# 顯示 AgGrid 表格
st.markdown("### 👇 點選並編輯欄位，完成後請按下方儲存")
grid_return = AgGrid(
    pd.DataFrame(users),
    gridOptions=options.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    height=380,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True
)

# 儲存變更
if st.button("💾 儲存變更"):
    updated_rows = grid_return["data"]
    for row in updated_rows.to_dict(orient="records"):
        user_id = row["id"]
        update_payload = {
            "is_admin": row["是否為管理員"],
            "is_active": row["使用者狀況"] == "啟用",
            "note": row.get("note") or ""
        }
        if row["使用者狀況"] == "刪除":
            requests.delete(f"https://ocr-whisper-production-2.up.railway.app/delete_user/{user_id}")
        else:
            requests.put(f"https://ocr-whisper-production-2.up.railway.app/update_user/{user_id}", json=update_payload)
    st.success("✅ 變更已儲存！請重新整理查看最新資料。")
