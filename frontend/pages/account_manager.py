import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼", layout="wide")
st.markdown("## 👩‍💼 帳號清單")

API_URL = "https://ocr-whisper-production-2.up.railway.app"

def fetch_users():
    try:
        response = requests.get(f"{API_URL}/users")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ 取得帳號資料失敗：{e}")
        return []

def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    # 檢查必要欄位是否存在
    required_cols = ["id", "username", "company", "is_admin", "status", "note"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠️ 回傳資料缺少欄位：{', '.join(missing_cols)}")
        return pd.DataFrame()

    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "company": "公司名稱",
        "is_admin": "是否為管理員",
        "status": "狀態",
        "note": "備註"
    })

    df["是否為管理員"] = df["是否為管理員"].astype(bool)

    def status_options(status):
        if status == "啟用中":
            return ["啟用中", "停用帳號", "刪除帳號"]
        elif status == "已停用":
            return ["已停用", "啟用帳號", "刪除帳號"]
        else:
            return [status]

    df["狀態選項"] = df["狀態"].apply(status_options)
    return df

def update_users(changes):
    for row in changes:
        user_id = row.get("使用者ID")
        status = row.get("狀態")
        note = row.get("備註")
        is_admin = row.get("是否為管理員")

        if status == "刪除帳號":
            requests.delete(f"{API_URL}/delete_user/{user_id}")
        elif status == "停用帳號":
            requests.put(f"{API_URL}/disable_user/{user_id}")
        elif status == "啟用帳號":
            requests.put(f"{API_URL}/enable_user/{user_id}")
        else:
            payload = {
                "note": note,
                "is_admin": is_admin
            }
            requests.put(f"{API_URL}/update_user/{user_id}", json=payload)

users = fetch_users()
df = process_users(users)

if df.empty:
    st.warning("⚠️ 尚無有效使用者資料，請稍後再試。")
    st.stop()

df["狀態選項"] = df["狀態選項"].apply(lambda x: x if isinstance(x, list) else [])

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("備註", editable=True)
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": []})
gb.configure_column("狀態選項", hide=True)

gridOptions = gb.build()

custom_js = JsCode("""
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
for col in gridOptions["columnDefs"]:
    if col["field"] == "狀態":
        col["cellEditorParams"] = custom_js

grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True,
    theme="streamlit",
    height=380,
    enable_enterprise_modules=False
)

with stylable_container("save-btn", css_styles="button {margin-top: 1rem;}"):
    if st.button("💾 儲存變更"):
        updated_rows = grid_response["data"]
        update_users(updated_rows.to_dict(orient="records"))
        st.success("✅ 已更新帳號資料！")

with stylable_container("back-btn", css_styles="button {margin-top: 1rem;}"):
    if st.button("🔙 返回主頁"):
        st.switch_page("首頁.py")
