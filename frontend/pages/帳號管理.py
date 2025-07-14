import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
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
        st.error(f"\U0001F6A8 錯誤：{e}")
    return []

def update_user(user_id, data):
    try:
        res = requests.put(f"{API_URL}/update_user/{user_id}", json=data)
        return res.status_code == 200
    except Exception as e:
        st.error(f"\u274C 更新失敗：{e}")
        return False

# ---------------------------
# UI Main Function
# ---------------------------
def main():
    st.markdown("<h1 style='color:#2c3e50;'>\U0001F468\u200D\U0001F4BC 帳號管理面板</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>可直接編輯表格欄位，或匯出帳號清單</p>", unsafe_allow_html=True)

    users = get_users()
    if not users:
        st.warning("\u26A0\uFE0F 尚無帳號資料")
        return

    df = pd.DataFrame(users)
    df["備註"] = df["note"].fillna("")
    df["公司"] = df["company_name"].fillna("")

    # 搜尋欄位
    search = st.text_input("\U0001F50D 搜尋帳號、公司或備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 匯出 CSV 按鈕
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="\U0001F4E4 匯出帳號清單 (CSV)",
        data=csv_buffer.getvalue(),
        file_name="user_list.csv",
        mime="text/csv",
    )

    # 顯示可編輯 AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("公司", editable=True)
    gb.configure_column("is_active", editable=True)
    gb.configure_column("is_admin", editable=True)
    gb.configure_selection("single", use_checkbox=True)

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        height=450,
        theme="streamlit",
        allow_unsafe_jscode=True
    )

    updated_df = grid["data"]
    selected = grid.get("selected_rows", [])

    # 若有選取且資料異動
    if selected and isinstance(selected, list) and len(selected) > 0:
        row = selected[0]
        user_id = row["id"]
        new_note = row.get("備註", "")
        new_active = row.get("is_active", False)
        new_admin = row.get("is_admin", False)
        new_company = row.get("公司", "")

        with st.expander("\U0001F6E0\uFE0F 編輯操作區"):
            st.write(f"✏️ 帳號：{row['username']} (ID: {user_id})")
            if st.button("\U0001F4BE 儲存變更"):
                payload = {
                    "note": new_note,
                    "active": new_active,
                    "is_admin": new_admin,
                    "company_name": new_company
                }
                if update_user(user_id, payload):
                    st.success("✅ 更新成功，請重新整理查看變更")
                else:
                    st.error("❌ 更新失敗")
    else:
        st.info("👈 請點選上方表格中一筆帳號資料進行操作")

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
        .stExpanderHeader {
            font-weight: bold;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

# 外部呼叫
def run():
    main()
