import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO

# ✅ 正確讀取 secrets 或顯示提示
if "API_BASE" in st.secrets:
    API_BASE = st.secrets["API_BASE"]
else:
    st.error("🚨 請至 Settings → Secrets 設定 API_BASE")
    st.stop()

# ---------------------------
# API Functions
# ---------------------------
def get_users():
    try:
        res = requests.get(f"{API_BASE}/users")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"🚨 錯誤：{e}")
    return []

def update_user(user_id, data):
    try:
        res = requests.put(f"{API_BASE}/update_user/{user_id}", json=data)
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 更新失敗：{e}")
        return False

def update_user_password(user_id, new_pw):
    try:
        res = requests.put(f"{API_BASE}/update_user_password/{user_id}", json={"password": new_pw})
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 密碼更新失敗：{e}")
        return False

# ---------------------------
# UI Main
# ---------------------------
st.title("👤 帳號管理面板")
st.caption("可直接在表格中編輯備註、角色、啟用狀態，或修改密碼")

users = get_users()
if not users:
    st.warning("⚠️ 尚無帳號資料")
    st.stop()

# 整理 DataFrame
for user in users:
    user["帳號"] = user.pop("username")
    user["備註"] = user.get("note") or ""
    user["角色"] = "管理員" if user.get("is_admin") else "一般使用者"
    user["啟用中"] = user.get("is_active", False)
    user["ID"] = user.get("id")

columns = ["ID", "帳號", "備註", "角色", "啟用中"]
df = pd.DataFrame(users)[columns]

# 分頁、搜尋欄
search = st.text_input("🔍 搜尋帳號 / 備註 / 角色")
if search:
    df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

# 建立 AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationPageSize=5)
gb.configure_default_column(editable=False, resizable=True, wrapText=True)
gb.configure_column("備註", editable=True)
gb.configure_column("啟用中", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": [True, False]})
gb.configure_column("角色", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": ["管理員", "一般使用者"]})
gb.configure_selection("multiple", use_checkbox=True)

grid = AgGrid(
    df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    height=460,
    theme="streamlit",
    fit_columns_on_grid_load=True,
)

updated_df = grid["data"]
selected_rows = grid["selected_rows"]

# 密碼欄
if selected_rows:
    for row in selected_rows:
        with st.expander(f"🔐 修改 {row['帳號']} 的密碼"):
            new_pw = st.text_input(f"輸入新密碼 - {row['帳號']}", type="password", key=f"pw_{row['ID']}")
            if st.button("💾 儲存密碼", key=f"pwbtn_{row['ID']}"):
                if update_user_password(row["ID"], new_pw):
                    st.success("✅ 密碼已更新")
                else:
                    st.error("❌ 更新失敗")

# 儲存所有更動
st.markdown("---")
if st.button("📥 儲存所有變更"):
    success = 0
    for i, row in updated_df.iterrows():
        user_id = row["ID"]
        payload = {
            "note": row["備註"],
            "active": row["啟用中"],
            "is_admin": True if row["角色"] == "管理員" else False
        }
        if update_user(user_id, payload):
            success += 1
    st.success(f"✅ 已更新 {success} 筆使用者資料")

# CSV 匯出
csv_buffer = BytesIO()
df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
st.download_button("📤 匯出帳號清單 (CSV)", csv_buffer.getvalue(), file_name="帳號清單.csv", mime="text/csv")

# 美化樣式
st.markdown("""
    <style>
    .ag-theme-streamlit .ag-root-wrapper {
        border-radius: 10px;
        font-size: 14px;
    }
    .stDownloadButton button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #f7f7f7;
    }
    </style>
""", unsafe_allow_html=True)
