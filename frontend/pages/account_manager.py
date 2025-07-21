import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from core.config import API_BASE

def go_home_button():
    st.markdown(
        """
        <div style='text-align: right; margin-bottom: 10px;'>
            <a href="/" style='text-decoration: none;'>
                <button style='padding: 6px 16px; font-size: 14px;'>🏠 返回主頁</button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# 權限檢查
if "access_token" not in st.session_state or st.session_state.get("role") != "admin":
    st.error("⚠️ 請先登入管理員帳號")
    st.stop()

st.set_page_config(page_title="帳號管理", layout="wide")
st.title("👤 帳號管理")
go_home_button()

# 搜尋欄
search_input = st.text_input("🔍 搜尋使用者帳號或 ID", "")

# 取得使用者清單
try:
    res = requests.get(f"{API_BASE}/users", headers={
        "Authorization": f"Bearer {st.session_state['access_token']}"
    })
    if res.status_code == 200:
        users = res.json()
    else:
        st.error("🚫 無法取得使用者清單")
        st.code(res.text)
        st.stop()
except Exception as e:
    st.error("❌ 發生錯誤")
    st.code(str(e))
    st.stop()

# 製作 DataFrame
df = pd.DataFrame(users)
if df.empty:
    st.warning("⚠️ 尚無使用者資料")
    st.stop()

if "role" not in df.columns:
    st.error("⚠️ 缺少 role 欄位，請確認後端 API")
    st.stop()

# 欄位轉換
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

# 搜尋過濾
if search_input:
    df = df[df["帳號"].str.contains(search_input, case=False) | df["ID"].astype(str).str.contains(search_input)]


# 加入操作欄位：根據啟用狀態決定選單
df["動作"] = df.apply(lambda row: "" if row["權限"] == "管理員" else (
    "啟用帳號" if row["啟用中"] == "停用" else "停用帳號"
), axis=1)

# AgGrid 設定
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_default_column(editable=True, wrapText=True, autoHeight=True, resizable=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)

# 欄位設定
gb.configure_column("ID", editable=False)
gb.configure_column("帳號", editable=True)
gb.configure_column("公司", editable=True)
gb.configure_column("備註", editable=True)
gb.configure_column("啟用中", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用", "停用"]})
gb.configure_column("權限", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["管理員", "使用者"]})
gb.configure_column("動作", cellEditor="agSelectCellEditor", cellEditorParams={"values": ["啟用帳號", "停用帳號", "刪除帳號", ""]})

# 欄位保護：禁止編輯管理員
for index, row in df.iterrows():
    if row["權限"] == "管理員":
        gb.configure_column("帳號", editable=False)
        gb.configure_column("公司", editable=False)
        gb.configure_column("備註", editable=False)
        gb.configure_column("啟用中", editable=False)
        gb.configure_column("權限", editable=False)
        gb.configure_column("動作", editable=False)

grid_options = gb.build()

# 顯示 AgGrid
st.markdown("### 👇 使用者清單（可編輯、可操作）")
grid = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MANUAL,
    fit_columns_on_grid_load=False,
    height=500,
    theme="streamlit"
)

selected = grid["selected_rows"]

# 密碼欄（若有選取帳號且不是管理員）
if selected:
    selected_row = selected[0]
    user_id = selected_row["ID"]
    is_admin = selected_row["權限"] == "管理員"
    st.markdown("---")
    st.subheader(f"🔐 修改密碼：{selected_row['帳號']}")

    if not is_admin:
        new_password = st.text_input("請輸入新密碼", type="password")
        if st.button("✅ 修改密碼"):
            if new_password.strip() == "":
                st.warning("請輸入新密碼")
            else:
                res = requests.put(f"{API_BASE}/update_user_password/{user_id}",
                    json={"new_password": new_password},
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"})
                if res.status_code == 200:
                    st.success("✅ 密碼修改成功")
                else:
                    st.error("❌ 修改失敗")
                    st.code(res.text)
    else:
        st.info("🔒 管理員帳號不允許修改密碼")

st.markdown("---")
if st.button("💾 儲存變更（欄位與狀態）"):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    error_count = 0

    for row in grid["data"]:
        user_id = row["ID"]
        if row["權限"] == "管理員":
            continue  # 管理員禁止修改

        # 狀態操作
        action = row.get("動作", "")
        try:
            if action == "停用帳號":
                requests.put(f"{API_BASE}/disable_user/{user_id}", headers=headers)
            elif action == "啟用帳號":
                requests.put(f"{API_BASE}/enable_user/{user_id}", headers=headers)
            elif action == "刪除帳號":
                requests.delete(f"{API_BASE}/delete_user/{user_id}", headers=headers)
        except Exception as e:
            st.error(f"❌ 執行 {action} 失敗：{row['帳號']}")
            error_count += 1

        # 欄位更新
        try:
            payload = {
                "username": row.get("帳號", ""),
                "company_name": row.get("公司", ""),
                "note": row.get("備註", ""),
                "is_active": row.get("啟用中") == "啟用",
                "role": "admin" if row.get("權限") == "管理員" else "user"
            }
            res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload, headers=headers)
            if res.status_code != 200:
                st.warning(f"❗ 帳號 {row['帳號']} 更新失敗：{res.text}")
                error_count += 1
        except Exception as e:
            st.error(f"❌ 帳號 {row.get('帳號')} 欄位更新錯誤")
            st.code(str(e))
            error_count += 1

    if error_count == 0:
        st.success("✅ 所有變更已儲存（請重新整理以更新畫面）")
    else:
        st.warning("⚠️ 有部分帳號操作失敗，請檢查上方訊息")
