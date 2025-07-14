import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from io import BytesIO

API_URL = "https://ocr-whisper-production-2.up.railway.app"

# ---------------------------
# API Functions
# ---------------------------
def get_users():
    try:
        res = requests.get(f"{API_URL}/users")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"🚨 錯誤：{e}")
    return []

def update_user(user_id, data):
    try:
        res = requests.put(f"{API_URL}/update_user/{user_id}", json=data)
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 更新失敗：{e}")
        return False

def delete_user(user_id):
    try:
        res = requests.delete(f"{API_URL}/delete_user/{user_id}")
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 刪除失敗：{e}")
        return False

# ---------------------------
# UI Main Function
# ---------------------------
def main():
    st.markdown("<h1 style='color:#2c3e50;'>👨‍💼 帳號管理面板</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>可查詢、編輯、停用或刪除帳號，並匯出成 Excel</p>", unsafe_allow_html=True)

    users = get_users()
    if not users:
        st.warning("⚠️ 尚無帳號資料")
        return

    df = pd.DataFrame(users)
    df["帳號狀態"] = df["is_active"].apply(lambda x: "🟢 啟用" if x else "🔴 停用")
    df["是否管理員"] = df["is_admin"].apply(lambda x: "✅ 是" if x else "❌ 否")
    df["備註"] = df["note"].fillna("")
    df["公司"] = df["company_name"].fillna("")

    display_df = df[["id", "username", "公司", "備註", "帳號狀態", "是否管理員"]]
    display_df.columns = ["ID", "帳號", "公司", "備註", "狀態", "管理員"]

    # 搜尋欄位
    search = st.text_input("🔍 搜尋帳號或備註")
    if search:
        display_df = display_df[display_df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 匯出按鈕
    csv_buffer = BytesIO()
    display_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="📤 匯出帳號清單 (CSV)",
        data=csv_buffer.getvalue(),
        file_name="user_list.csv",
        mime="text/csv",
    )

    # AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_selection("single")
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    grid = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=400,
        theme="streamlit",
    )

    selected = grid["selected_rows"]
    if selected:
        row = selected[0]
        user_id = row["ID"]
        username = row["帳號"]

        st.markdown("---")
        st.markdown(f"<h4 style='color:#34495e;'>🛠️ 編輯帳號：{username} (ID: {user_id})</h4>", unsafe_allow_html=True)

        new_note = st.text_input("✏️ 備註內容", value=row["備註"])
        new_password = st.text_input("🔐 新密碼（可留空）", type="password")
        active = st.checkbox("✅ 是否啟用", value=row["狀態"] == "🟢 啟用")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 儲存變更"):
                update_data = {"note": new_note, "active": active}
                if new_password:
                    update_data["password"] = new_password
                success = update_user(user_id, update_data)
                if success:
                    st.success("✅ 已成功更新")
                else:
                    st.error("❌ 更新失敗")

        with col2:
            if st.button("🗑️ 刪除帳號"):
                if st.checkbox("⚠️ 確認永久刪除"):
                    if delete_user(user_id):
                        st.success("✅ 已刪除帳號")
                    else:
                        st.error("❌ 刪除失敗")

    # 自訂 CSS 美化
    st.markdown("""
        <style>
        .stTextInput>div>div>input {
            background-color: #f4f4f4;
            border-radius: 6px;
        }
        .stDownloadButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# 外部呼叫用
def run():
    main()
