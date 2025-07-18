import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from core.config import API_BASE

# 🔧 內建返回主頁按鈕（避免 import error）
def go_home_button():
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <a href="/"><button style="padding:6px 12px;font-size:14px;">🏠 返回主頁</button></a>
        </div>
    """, unsafe_allow_html=True)

# ✅ 設定頁面與權限檢查
st.set_page_config(page_title="帳號管理", layout="wide")
if not st.session_state.get("access_token") or st.session_state.get("role") != "admin":
    st.error("⚠️ 請先登入")
    st.stop()

st.title("👤 帳號管理")
go_home_button()

# ✅ 取得使用者清單
try:
    res = requests.get(f"{API_BASE}/users", headers={
        "Authorization": f"Bearer {st.session_state['access_token']}"
    })
    if res.status_code == 200:
        users = res.json()
    else:
        st.error("🚫 無法取得使用者清單")
        st.stop()
except Exception as e:
    st.error("❌ 錯誤")
    st.code(str(e))
    st.stop()

# ✅ 資料轉換為 DataFrame 並處理欄位
df = pd.DataFrame(users)
if df.empty:
    st.warning("⚠️ 尚無使用者資料")
    st.stop()

df = df.rename(columns={
    "id": "ID",
    "username": "帳號",
    "company_name": "公司",
    "note": "備註",
    "is_active": "啟用中",
    "role": "權限"
})
df["啟用中"] = df["啟用中"].map({True: "啟用", False: "停用"})
df["權限"] = df["權限"].map({"admin": "管理員", "user": "使用者"})

# ✅ 建立 AgGrid 表格（可編輯＋多選）
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_column("ID", editable=False)
gb.configure_column("啟用中", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用", "停用"]})
gb.configure_column("權限", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["管理員", "使用者"]})
grid_options = gb.build()

st.markdown("### 👇 使用者清單（可編輯）")
grid = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MANUAL,
    fit_columns_on_grid_load=True,
    height=380,
    theme="streamlit"
)

updated_rows = grid["data"]
selected_rows = grid["selected_rows"]

# ✅ 儲存變更按鈕
if st.button("💾 儲存變更"):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    for row in selected_rows:
        user_id = row["ID"]
        payload = {
            "username": row["帳號"],
            "company_name": row["公司"],
            "note": row["備註"],
            "is_active": row["啟用中"] == "啟用",
            "role": "admin" if row["權限"] == "管理員" else "user"
        }
        try:
            res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload, headers=headers)
            if res.status_code != 200:
                st.warning(f"❗ 帳號 {row['帳號']} 更新失敗：{res.text}")
        except Exception as e:
            st.error(f"❌ 帳號 {row['帳號']} 更新錯誤")
            st.code(str(e))
    st.success("✅ 所有變更已儲存")
    st.rerun()
