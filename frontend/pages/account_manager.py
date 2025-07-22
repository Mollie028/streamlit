import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import requests
from utils.auth import is_logged_in, logout_button

st.set_page_config(page_title="帳號管理", page_icon="🧑‍💼")

# 登入檢查
if not is_logged_in():
    st.stop()

# 標題區
st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h2>🧑‍💼 帳號管理</h2>
        <a href="/" style="text-decoration: none;">
            <button style="padding: 0.5rem 1rem; background-color: #eee; border: 1px solid #ccc; border-radius: 5px;">← 返回首頁</button>
        </a>
    </div>
    <hr>
""", unsafe_allow_html=True)

# API URL（請確認是否一致）
API_URL = "https://ocr-whisper-production-2.up.railway.app"

# 取得目前使用者資訊（用於權限判斷）
current_user = st.session_state.get("user")
is_admin = current_user.get("is_admin", False)

# 載入使用者清單
def load_users():
    try:
        response = requests.get(f"{API_URL}/users")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"載入使用者時發生錯誤：{e}")
        return []

users = load_users()

# 中文欄位名稱轉換與處理
for user in users:
    user["使用者 ID"] = user.pop("id")
    user["使用者帳號"] = user.pop("username")
    user["是否為管理員"] = user.pop("is_admin")
    user["使用者狀況"] = "啟用" if user.pop("is_active") else "停用"
    user["備註"] = user.get("note", "")

# 建立表格設定
options = GridOptionsBuilder.from_dataframe(pd.DataFrame(users))
options.configure_column("使用者 ID", editable=False)
options.configure_column("使用者帳號", editable=False)
options.configure_column("是否為管理員", editable=is_admin)
options.configure_column("備註", editable=is_admin)
options.configure_column(
    "使用者狀況",
    editable=is_admin,
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": ["啟用", "停用", "刪除"]},
)
options.configure_grid_options(domLayout='normal')

# 顯示表格
st.markdown("#### 使用者帳號清單")
response = AgGrid(
    pd.DataFrame(users),
    gridOptions=options.build(),
    update_mode=GridUpdateMode.MANUAL,
    height=380,
    theme="alpine",
    fit_columns_on_grid_load=True
)

# 儲存按鈕
if is_admin and st.button("💾 儲存變更"):
    updated = response["data"]
    for u in updated:
        user_id = u["使用者 ID"]
        status = u["使用者狀況"]
        update_payload = {
            "username": u["使用者帳號"],
            "is_admin": u["是否為管理員"],
            "note": u["備註"]
        }

        # 狀態操作
        if status == "啟用":
            requests.put(f"{API_URL}/enable_user/{user_id}")
        elif status == "停用":
            requests.put(f"{API_URL}/disable_user/{user_id}")
        elif status == "刪除":
            requests.delete(f"{API_URL}/delete_user/{user_id}")

        # 更新其他欄位（如是管理員、備註）
        requests.put(f"{API_URL}/update_user/{user_id}", json=update_payload)

    st.success("使用者資料已更新！請重新整理以查看結果。")

# 登出按鈕
logout_button()
