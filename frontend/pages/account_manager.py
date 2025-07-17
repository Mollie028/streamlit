import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼", layout="wide")
st.markdown("## 👩‍💼 帳號清單")

API_URL = "https://ocr-whisper-production-2.up.railway.app"

# 取得帳號資料
def fetch_users():
    try:
        response = requests.get(f"{API_URL}/users")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ 取得帳號資料失敗：{e}")
        return []

# 整理為 DataFrame
def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "company_name": "公司名稱",
        "is_admin": "是否為管理員",
        "is_active": "帳號啟用",
        "note": "備註"
    })

    # 顯示中文狀態
    df["狀態"] = df["帳號啟用"].apply(lambda x: "啟用中" if x else "停用帳號")
    df["是否為管理員"] = df["是否為管理員"].astype(bool)

    # 動態下拉選單邏輯
    def status_options(status):
        if status == "啟用中":
            return ["停用帳號", "刪除帳號"]
        elif status == "停用帳號":
            return ["啟用帳號", "刪除帳號"]
        else:
            return []

    df["狀態選項"] = df["狀態"].apply(status_options)
    return df

# 發送變更請求
def update_users(changes):
    success_count = 0
    for row in changes:
        user_id = row.get("使用者ID")
        is_admin = row.get("是否為管理員", False)
        note = row.get("備註", "")
        status = row.get("狀態")

        # 狀態處理
        if status == "刪除帳號":
            requests.delete(f"{API_URL}/delete_user/{user_id}")
        elif status == "停用帳號":
            requests.put(f"{API_URL}/disable_user/{user_id}")
        elif status == "啟用帳號":
            requests.put(f"{API_URL}/enable_user/{user_id}")

        # 更新管理員與備註
        payload = {
            "is_admin": is_admin,
            "note": note
        }
        requests.put(f"{API_URL}/update_user/{user_id}", json=payload)
        success_count += 1
    return success_count

# 主要流程
users = fetch_users()
df = process_users(users)

if df.empty:
    st.warning("⚠️ 尚無有效使用者資料，請稍後再試。")
    st.stop()

# 設定 AgGrid 表格
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("備註", editable=True)
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": []})
gb.configure_column("帳號啟用", hide=True)
gb.configure_column("狀態選項", hide=True)

# 動態 JS：依每列狀態變化產生下拉選單
custom_js = JsCode("""
function(params) {
    if (params.data && params.data['狀態選項']) {
        return {
            values: params.data['狀態選項']
        }
    }
    return { values: [] }
}
""")
for col in gb.build()["columnDefs"]:
    if col["field"] == "狀態":
        col["cellEditorParams"] = custom_js

grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True,
    theme="streamlit",
    height=400
)

# 儲存變更
with stylable_container("save-btn", css_styles="button {margin-top: 1rem;}"):
    if st.button("💾 儲存變更"):
        updated_rows = grid_response["data"]
        changes = updated_rows.to_dict(orient="records")
        count = update_users(changes)
        st.success(f"✅ 已成功儲存 {count} 筆變更！")

# 返回首頁
with stylable_container("back-btn", css_styles="button {margin-top: 1rem;}"):
    if st.button("🔙 返回主頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
