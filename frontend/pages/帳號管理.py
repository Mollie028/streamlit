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
    st.markdown("<p style='color:gray;'>可編輯帳號資料，點選一列後可儲存／停用／刪除</p>", unsafe_allow_html=True)

    users = get_users()
    if not users:
        st.warning("⚠️ 尚無帳號資料")
        return

    df = pd.DataFrame(users)

    # ✅ 加上中文欄位顯示
    df = df.rename(columns={
        "id": "ID",
        "username": "帳號",
        "is_admin": "管理員",
        "company_name": "公司",
        "is_active": "啟用中",
        "note": "備註",
    })

    # ✅ 處理空值
    df["備註"] = df["備註"].fillna("")
    df["公司"] = df["公司"].fillna("")

    # 🔍 搜尋欄位
    search = st.text_input("🔍 搜尋帳號、公司或備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 📤 匯出 CSV
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="📤 匯出帳號清單 (CSV)",
        data=csv_buffer.getvalue(),
        file_name="帳號清單.csv",
        mime="text/csv",
    )

    # ✅ 設定 AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("啟用中", editable=True)
    gb.configure_column("管理員", editable=True)
    gb.configure_selection("single", use_checkbox=True)

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=450,
        theme="streamlit",
    )

    updated_df = grid["data"]
    selected = grid.get("selected_rows", [])

    # ✅ 避免 ValueError：DataFrame 的布林轉換問題
    if selected and isinstance(selected, list):
        row = selected[0]
        user_id = row["ID"]
        new_note = row["備註"]
        new_active = row["啟用中"]
        new_admin = row["管理員"]

        with st.expander("🛠️ 編輯操作區", expanded=True):
            st.write(f"✏️ 帳號：**{row['帳號']}** (ID: `{user_id}`)")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("💾 儲存變更"):
                    payload = {
                        "note": new_note,
                        "active": new_active,
                        "is_admin": new_admin
                    }
                    if update_user(user_id, payload):
                        st.success("✅ 已更新成功，請重新整理查看")
                    else:
                        st.error("❌ 更新失敗")

            with col2:
                if st.button("🛑 停用帳號"):
                    if update_user(user_id, {"active": False}):
                        st.success("✅ 該帳號已停用")
                    else:
                        st.error("❌ 停用失敗")

            with col3:
                if st.button("🗑️ 刪除帳號"):
                    confirm = st.warning("⚠️ 確定要刪除嗎？此動作無法復原", icon="⚠️")
                    if delete_user(user_id):
                        st.success("🗑️ 已成功刪除該帳號，請重新整理")
                    else:
                        st.error("❌ 刪除失敗")

    # 🖌️ CSS 美化
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

# 🌐 外部呼叫
def run():
    main()
