import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_extras.stylable_container import stylable_container

API_URL = "https://ocr-whisper-production-2.up.railway.app"

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼", layout="wide")
st.markdown("## 👩‍💼 帳號清單")

# 🧩 限管理員才能進入
current_user = st.session_state.get("user_info", {})
if not current_user.get("is_admin", False):
    st.warning("此頁面僅限管理員使用")
    st.stop()

# 📦 抓取使用者資料
def fetch_users():
    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"無法取得使用者資料：{e}")
        return []

# 🔧 資料轉換與欄位建立
def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df
    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "company_name": "公司名稱",
        "is_admin": "是否為管理員",
        "is_active": "啟用狀態",
        "note": "備註"
    })
    df["是否為管理員"] = df["是否為管理員"].astype(bool)
    df["啟用狀態"] = df["啟用狀態"].astype(bool)
    df["狀態"] = df["啟用狀態"].apply(lambda x: "啟用中" if x else "已停用")
    df["狀態選項"] = df["狀態"].apply(lambda x: ["停用帳號", "刪除帳號"] if x == "啟用中" else ["啟用帳號", "刪除帳號"])
    return df

# 🚀 主流程
users = fetch_users()
df = process_users(users)

if df.empty:
    st.info("尚無有效使用者資料，請稍後再試。")
    st.stop()

# 📊 表格欄位設定
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("備註", editable=True)
gb.configure_column("狀態選項", hide=True)

# ✅ 動態下拉選單 JS 實作
cell_editor_js = JsCode("""
function(params) {
    if (params.data && params.data['狀態選項']) {
        return {
            values: params.data['狀態選項']
        }
    }
    return {
        values: []
    }
}
""")

gb.configure_column(
    "狀態",
    editable=True,
    cellEditor="agSelectCellEditor",
    cellEditorParams=cell_editor_js
)

# 📋 顯示表格
grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True,
    theme="streamlit",
    height=400,
    allow_unsafe_jscode=True
)

updated_rows = grid_response["data"].to_dict("records")

# 💾 儲存變更
with stylable_container("save", css_styles="margin-top: 20px"):
    if st.button("📄 儲存變更"):
        success_count = 0
        for row in updated_rows:
            uid = row.get("使用者ID")
            is_admin = row.get("是否為管理員", False)
            note = row.get("備註", "")
            status_text = row.get("狀態")

            try:
                if status_text == "刪除帳號":
                    requests.delete(f"{API_URL}/delete_user/{uid}")
                elif status_text == "停用帳號":
                    requests.put(f"{API_URL}/disable_user/{uid}")
                elif status_text == "啟用帳號":
                    requests.put(f"{API_URL}/enable_user/{uid}")
                else:
                    payload = {"is_admin": is_admin, "note": note}
                    requests.put(f"{API_URL}/update_user/{uid}", json=payload)
                success_count += 1
            except:
                st.error(f"❌ 帳號 ID {uid} 更新失敗")

        st.success(f"✅ 已成功儲存 {success_count} 筆資料變更")
        st.session_state["current_page"] = "account_manage"
        st.rerun()

# 🔙 返回主頁
with stylable_container("back", css_styles="margin-top: 10px"):
    if st.button("🔙 返回主頁"):
        st.session_state["current_page"] = "home"
        st.rerun()

# ✅ run() 支援 app.py 呼叫
def run():
    pass
