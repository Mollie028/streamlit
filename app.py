import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.stylable_container import stylable_container

# 網站基礎 URL
API_URL = "https://ocr-whisper-production-2.up.railway.app"

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼", layout="wide")
st.markdown("## 👩‍💼 帳號清單")

# 抓取使用者資料
def fetch_users():
    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"無法抓取使用者資料：{e}")
        return []

# 處理資料
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

    # 增加 "狀態" 變數顯示
    df["狀態"] = df["啟用狀態"].apply(lambda x: "啟用中" if x else "已停用")

    # 增加狀態下拉選項（加入動態狀態變化）
    def get_options(val):
        return ["啟用中", "停用帳號", "刪除帳號"] if val else ["已停用", "啟用帳號", "刪除帳號"]

    df["狀態選項"] = df["啟用狀態"].apply(get_options)

    return df

# 登記使用者
current_user = st.session_state.get("user_info", {})
is_admin = current_user.get("is_admin", False)
current_user_id = current_user.get("id")

# 預防非管理者試圖進入
if not is_admin:
    st.warning("此頁面僅限管理員使用")
    st.stop()

users = fetch_users()
df = process_users(users)

if df.empty:
    st.info("還沒有任何使用者資料")
    st.stop()

# 建立 AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
gb.configure_column("備註", editable=True)
gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor")
gb.configure_column("狀態選項", hide=True)

gridOptions = gb.build()

# 替換欄位選項
for col in gridOptions["columnDefs"]:
    if col["field"] == "狀態":
        col["cellEditorParams"] = {
            "function": "params => { return { values: params.data['狀態選項'] } }"
        }

# 顯示表格
grid = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True,
    theme="streamlit",
    height=400,
    allow_unsafe_jscode=True
)

updated_rows = grid["data"].to_dict("records")

# 採用 button 檢查並送出編輯資料
with stylable_container("save", css_styles="margin-top: 20px"):
    if st.button("📄 儲存變更"):
        success_count = 0
        for row in updated_rows:
            uid = row.get("使用者ID")
            is_admin = row.get("是否為管理員", False)
            note = row.get("備註", "")
            status_text = row.get("狀態")

            # 變更狀態
            if status_text == "刪除帳號":
                requests.delete(f"{API_URL}/delete_user/{uid}")
            elif status_text == "停用帳號":
                requests.put(f"{API_URL}/disable_user/{uid}")
            elif status_text == "啟用帳號":
                requests.put(f"{API_URL}/enable_user/{uid}")
            else:
                # 修改備註和管理設定
                payload = {
                    "is_admin": is_admin,
                    "note": note
                }
                requests.put(f"{API_URL}/update_user/{uid}", json=payload)

            success_count += 1

        st.success(f"✅ 已成功儲存 {success_count} 筆資料變更")
        st.rerun()

# 返回主頁
with stylable_container("back", css_styles="margin-top: 10px"):
    if st.button("🔙 返回主頁"):
        st.session_state["current_page"] = "home"
        st.rerun()

# ✅ 將功能包裝為 run()
def run():
    pass
