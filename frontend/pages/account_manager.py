import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼", layout="wide")
st.markdown("## 👩‍💼 帳號清單")

# 🔹API 位置
API_URL = "https://ocr-whisper-production-2.up.railway.app"

# 🔹取得帳號資料
def fetch_users():
    try:
        response = requests.get(f"{API_URL}/users")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ 取得帳號資料失敗：{e}")
        return []

# 🔹轉換為 DataFrame
def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    # ✅ 檢查欄位是否缺失，補上預設值
    for col in ["id", "username", "company", "is_admin", "status", "note"]:
        if col not in df.columns:
            df[col] = ""

    # ✅ 欄位轉中文
    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "company": "公司名稱",
        "is_admin": "是否為管理員",
        "status": "狀態",
        "note": "備註"
    })

    # ✅ 格式處理
    df["是否為管理員"] = df["是否為管理員"].astype(bool)
    df["狀態"] = df["狀態"].fillna("未知").astype(str)
    df["備註"] = df["備註"].fillna("").astype(str)

    # ✅ 狀態選項邏輯
    def get_status_options(status):
        if status == "啟用中":
            return ["啟用中", "停用帳號", "刪除帳號"]
        elif status == "已停用":
            return ["已停用", "啟用帳號", "刪除帳號"]
        else:
            return [status]

    df["狀態選項"] = df["狀態"].apply(get_status_options)

    return df

# 🔹發送更新請求
def update_users(changes):
    for row in changes:
        user_id = row.get("使用者ID")
        status = row.get("狀態")
        note = row.get("備註")
        is_admin = row.get("是否為管理員")

        try:
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
        except Exception as e:
            st.error(f"❌ 使用者 {user_id} 更新失敗：{e}")

# 🔹主程式
users = fetch_users()
df = process_users(users)

if df.empty:
    st.warning("⚠️ 尚無使用者資料。")
    st.stop()

# ✅ 設定 GridOptions
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("備註", editable=True)
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": []})
gb.configure_column("狀態選項", hide=True)

gridOptions = gb.build()

# ✅ JS 動態設定下拉選單內容
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

# ✅ 顯示 AgGrid
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True,
    theme="streamlit",
    height=380,
    allow_unsafe_jscode=True
)

# ✅ 儲存變更按鈕
with stylable_container("save-btn", css_styles="button {margin-top: 1rem;}"):
    if st.button("💾 儲存變更"):
        updated_rows = grid_response["data"]
        update_users(updated_rows.to_dict(orient="records"))
        st.success("✅ 已更新帳號資料！")

# ✅ 返回主頁按鈕
with stylable_container("back-btn", css_styles="button {margin-top: 1rem;}"):
    if st.button("🔙 返回主頁"):
        st.switch_page("首頁.py")
