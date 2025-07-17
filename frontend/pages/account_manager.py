import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode

API_URL = "https://ocr-whisper-production-2.up.railway.app"

# ✅ 權限檢查：非管理員禁止進入
if not st.session_state.get("user_info", {}).get("is_admin", False):
    st.error("🚫 無權限存取此頁面")
    st.stop()

st.set_page_config(page_title="帳號管理", page_icon="👤", layout="wide")
st.title("👤 帳號清單")

# 🔹 取得使用者清單
def fetch_users():
    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"❌ 無法取得使用者資料：{e}")
        return []

users = fetch_users()
if not users:
    st.stop()

# 🔹 整理成表格格式
for u in users:
    u["使用者ID"] = u.get("id", "")
    u["帳號名稱"] = u.get("username", "")
    u["是否為管理員"] = u.get("is_admin", False)
    u["公司名稱"] = u.get("company", "") or u.get("company_name", "")
    u["備註"] = u.get("note", "")
    u["狀態"] = "啟用中" if u.get("is_active", True) else "已停用"

    # 🔸 動態狀態選單
    if u["狀態"] == "啟用中":
        u["狀態選項"] = ["啟用中", "停用帳號", "刪除帳號"]
    elif u["狀態"] == "已停用":
        u["狀態選項"] = ["已停用", "啟用帳號", "刪除帳號"]
    else:
        u["狀態選項"] = [u["狀態"]]

df = pd.DataFrame(users)[["使用者ID", "帳號名稱", "公司名稱", "是否為管理員", "狀態", "備註", "狀態選項"]]

# 🔹 AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("備註", editable=True)
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": []})
gb.configure_column("狀態選項", hide=True)

# 🔹 動態 JS 注入下拉選單
js = JsCode("""
function(params) {
    if (params.data && params.data['狀態選項']) {
        return {
            values: params.data['狀態選項']
        }
    }
    return { values: [] }
}
""")
grid_options = gb.build()
for col in grid_options["columnDefs"]:
    if col["field"] == "狀態":
        col["cellEditorParams"] = js

# 🔹 顯示表格
grid_return = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme="streamlit",
    height=380,
    allow_unsafe_jscode=True
)

# 🔹 點擊儲存變更
if st.button("💾 儲存變更"):
    updated_df = grid_return["data"]
    success = 0
    for row in updated_df.itertuples(index=False):
        user_id = row.使用者ID
        payload = {
            "note": row.備註,
            "is_admin": row.是否為管理員
        }

        # 狀態更新
        if row.狀態 == "啟用帳號":
            requests.put(f"{API_URL}/enable_user/{user_id}")
        elif row.狀態 == "停用帳號":
            requests.put(f"{API_URL}/disable_user/{user_id}")
        elif row.狀態 == "刪除帳號":
            requests.delete(f"{API_URL}/delete_user/{user_id}")

        # 備註與權限更新
        requests.put(f"{API_URL}/update_user/{user_id}", json=payload)
        success += 1

    st.success(f"✅ 已成功儲存 {success} 筆變更！")
    st.experimental_rerun()

# 🔙 返回主頁
if st.button("🔙 返回主頁"):
    st.session_state["current_page"] = "home"
    st.rerun()
