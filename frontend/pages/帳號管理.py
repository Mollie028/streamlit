import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
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

# ---------------------------
# UI Main Function
# ---------------------------
def main():
    st.markdown("<h1 style='color:#2c3e50;'>👨‍💼 帳號管理面板</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>可直接編輯表格欄位，或匯出帳號清單</p>", unsafe_allow_html=True)

    users = get_users()
    if not users:
        st.warning("⚠️ 尚無帳號資料")
        return

    df = pd.DataFrame(users)
    df["備註"] = df["note"].fillna("")
    df["公司"] = df["company_name"].fillna("")

    # 搜尋欄位
    search = st.text_input("🔍 搜尋帳號、公司或備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 匯出 CSV 按鈕
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="📤 匯出帳號清單 (CSV)",
        data=csv_buffer.getvalue(),
        file_name="user_list.csv",
        mime="text/csv",
    )

    # 顯示可編輯 AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("is_active", editable=True)
    gb.configure_column("is_admin", editable=True)
    gb.configure_selection("single", use_checkbox=True)

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=450,
        theme="streamlit",
    )

    updated_df = grid["data"]
    selected = grid["selected_rows"]

    # 若有選取且資料異動
    if selected:
        row = selected[0]
        user_id = row["id"]
        new_note = row["備註"]
        new_active = row["is_active"]
        new_admin = row["is_admin"]

        with st.expander("🛠️ 編輯操作區"):
            st.write(f"✏️ 帳號：{row['username']} (ID: {user_id})")
            if st.button("💾 儲存變更"):
                payload = {
                    "note": new_note,
                    "active": new_active,
                    "is_admin": new_admin
                }
                if update_user(user_id, payload):
                    st.success("✅ 更新成功，請重新整理查看變更")
                else:
                    st.error("❌ 更新失敗")

    # CSS 美化
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
        .ag-root-wrapper {
            border-radius: 6px;
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

# 外部呼叫
def run():
    main()
