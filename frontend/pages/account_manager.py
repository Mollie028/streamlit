import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import requests
from services.auth_service import is_logged_in, logout_button
from core.config import API_BASE

# ✅ 登入狀態與權限檢查
user_info = is_logged_in()
if not isinstance(user_info, dict) or "is_admin" not in user_info:
    st.error("登入狀態錯誤，請重新登入")
    st.stop()
if not user_info["is_admin"]:
    st.error("您沒有權限觀看此頁面。")
    st.stop()

# ✅ 頁面標題
st.markdown("## 🧑‍💼 使用者帳號清單")
st.markdown("以下為所有使用者帳號資料，僅限管理員修改")

# ✅ 返回主頁按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")

# ✅ 登出按鈕
logout_button()

# ✅ 取得所有使用者資料
response = requests.get(f"{API_BASE}/users")
if response.status_code != 200:
    st.error("無法取得使用者資料")
    st.stop()
users = response.json()

# ✅ 欄位轉換
for user in users:
    user["使用者帳號"] = user["username"]
    user["是否為管理員"] = user["is_admin"]
    user["使用者狀況"] = "啟用" if user["is_active"] else "停用"

# ✅ 建立 DataFrame（並固定欄位順序）
df = pd.DataFrame(users)[["id", "使用者帳號", "是否為管理員", "使用者狀況", "note"]]

# ✅ AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)
gb.configure_column("id", header_name="ID", editable=False, pinned="left", width=80)
gb.configure_column("使用者帳號", editable=False, pinned="left", width=200)
gb.configure_column("是否為管理員", cellEditor="agCheckboxCellEditor", width=130)
gb.configure_column("note", header_name="備註", width=200)

# ✅ 使用者狀況下拉選單（點一下即展開）
js_code = JsCode('''
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
        getGui() { return this.eInput; }
        afterGuiAttached() { this.eInput.focus(); }
        getValue() { return this.eInput.value; }
        destroy() {}
        isPopup() { return false; }
    }
''')
gb.configure_column("使用者狀況", cellEditorJsCode=js_code, width=120)

# ✅ 其他設定
gb.configure_grid_options(domLayout='normal')
gb.configure_grid_options(suppressCellFocus=False)
gb.configure_grid_options(rowSelection='multiple')
gb.configure_grid_options(suppressRowClickSelection=False)
gb.configure_grid_options(alwaysShowHorizontalScroll=True)
gb.configure_grid_options(suppressMovableColumns=True)
gb.configure_grid_options(pagination=True, paginationPageSize=5)

# ✅ 顯示表格
st.markdown("### 👇 點選並編輯欄位，完成後請按下方儲存")
grid_return = AgGrid(
    df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    height=380,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True
)

# ✅ 儲存變更
if st.button("💾 儲存變更"):
    updated_rows = grid_return["data"]
    for row in updated_rows.to_dict(orient="records"):
        user_id = row["id"]
        status = row["使用者狀況"]

        if status == "刪除":
            requests.delete(f"{API_BASE}/delete_user/{user_id}")
        else:
            payload = {
                "is_admin": row["是否為管理員"],
                "is_active": status == "啟用",
                "note": row.get("note", "")
            }
            requests.put(f"{API_BASE}/update_user/{user_id}", json=payload)

    st.success("✅ 資料已更新，請重新整理查看最新狀態")
