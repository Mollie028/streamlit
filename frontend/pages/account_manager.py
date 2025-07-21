import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from core.config import API_BASE

st.markdown("""<h2 style='text-align: center;'>👥 帳號管理</h2>""", unsafe_allow_html=True)
st.divider()

# 權限檢查與初始化
access_token = st.session_state.get("access_token")
current_user = st.session_state.get("user", {})
is_admin = current_user.get("role") == "admin"
headers = {"Authorization": f"Bearer {access_token}"}

# 取得使用者資料
try:
    res = requests.get(f"{API_BASE}/users", headers=headers)
    users_data = res.json()
except Exception as e:
    st.error("無法取得使用者清單")
    st.stop()

if not isinstance(users_data, list):
    st.warning("目前無任何使用者資料。")
    st.stop()

# 建立 DataFrame 並整理欄位
df = pd.DataFrame(users_data)
df = df[["id", "username", "is_active", "role", "note"]]
df.rename(columns={
    "id": "使用者ID",
    "username": "帳號",
    "is_active": "啟用中",
    "role": "角色",
    "note": "備註"
}, inplace=True)

# 欄位格式轉換
role_options = ["user", "admin"]
df["啟用中"] = df["啟用中"].apply(lambda x: "是" if x else "否")

# 搜尋功能
with st.expander("🔍 搜尋帳號"):
    keyword = st.text_input("請輸入帳號或使用者 ID")
    if keyword:
        df = df[df["帳號"].str.contains(keyword) | df["使用者ID"].astype(str).str.contains(keyword)]

# 建立 AgGrid 表格
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection("multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
gb.configure_grid_options(domLayout='normal')
gb.configure_default_column(editable=True)
gb.configure_column("帳號", editable=False)
gb.configure_column("使用者ID", editable=False)
gb.configure_column("啟用中", cellEditor='agSelectCellEditor', cellEditorParams={'values': ["是", "否"]})
gb.configure_column("角色", cellEditor='agSelectCellEditor', cellEditorParams={'values': role_options})
gb.configure_column("備註", editable=True)

grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    height=380,
    reload_data=True,
)

# 取得修改後的資料與選取列
updated_df = grid_response["data"]
selected_rows = grid_response["selected_rows"]

# 密碼修改區塊
with st.expander("🔑 修改密碼"):
    target_username = st.text_input("請輸入要修改密碼的帳號")
    new_pass = st.text_input("新密碼", type="password")
    if st.button("儲存新密碼"):
        if not target_username or not new_pass:
            st.warning("請輸入帳號與新密碼")
        elif target_username == current_user.get("username") or is_admin:
            try:
                user_res = requests.get(f"{API_BASE}/users", headers=headers)
                all_users = user_res.json()
                matched = [u for u in all_users if u["username"] == target_username]
                if matched:
                    user_id = matched[0]["id"]
                    res = requests.put(f"{API_BASE}/update_user_password/{user_id}",
                                       json={"new_password": new_pass},
                                       headers=headers)
                    if res.status_code == 200:
                        st.success("✅ 密碼修改成功")
                    else:
                        st.error("❌ 修改失敗")
                else:
                    st.warning("查無此帳號")
            except Exception as e:
                st.error("❌ 系統錯誤")
                st.code(str(e))
        else:
            st.warning("您沒有修改此帳號的權限")

# 儲存變更按鈕
if st.button("💾 儲存所有變更"):
    for _, row in updated_df.iterrows():
        user_id = row["使用者ID"]
        if row["帳號"] == "admin":
            continue  # 不允許修改管理員帳號
        payload = {
            "is_active": row["啟用中"] == "是",
            "role": row["角色"],
            "note": row["備註"]
        }
        try:
            res = requests.put(f"{API_BASE}/update_user/{user_id}", json=payload, headers=headers)
            if res.status_code != 200:
                st.error(f"更新 {row['帳號']} 失敗：{res.text}")
        except Exception as e:
            st.error(f"更新 {row['帳號']} 發生錯誤")
            st.code(str(e))
    st.success("✅ 所有變更已儲存")

# 批次操作
st.markdown("""<h4 style='margin-top:30px;'>⚙️ 批次操作（請先勾選帳號）</h4>""", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    action = st.selectbox("請選擇操作", ["無", "啟用帳號", "停用帳號", "刪除帳號"])
with col2:
    if st.button("🚀 執行批次操作"):
        if not selected_rows:
            st.warning("請先勾選至少一筆帳號")
        for row in selected_rows:
            user_id = row["使用者ID"]
            if row["帳號"] == "admin":
                st.warning("無法操作管理員帳號")
                continue
            try:
                if action == "啟用帳號":
                    res = requests.put(f"{API_BASE}/enable_user/{user_id}", headers=headers)
                elif action == "停用帳號":
                    res = requests.put(f"{API_BASE}/disable_user/{user_id}", headers=headers)
                elif action == "刪除帳號":
                    res = requests.delete(f"{API_BASE}/delete_user/{user_id}", headers=headers)
                if res.status_code == 200:
                    st.success(f"✅ {row['帳號']} 執行 {action} 成功")
                else:
                    st.warning(f"❌ {row['帳號']} 操作失敗：{res.text}")
            except Exception as e:
                st.error(f"❌ {row['帳號']} 操作錯誤")
                st.code(str(e))
