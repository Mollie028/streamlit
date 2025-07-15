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

def update_password(user_id, new_password):
    try:
        res = requests.put(
            f"{API_URL}/update_user_password/{user_id}",
            json={"password": new_password}
        )
        return res.status_code == 200
    except Exception as e:
        st.error(f"❌ 密碼更新失敗：{e}")
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
    st.markdown("<p style='color:gray;'>可編輯帳號資料，勾選一筆或多筆後可儲存 / 停用 / 修改密碼 / 刪除</p>", unsafe_allow_html=True)

    users = get_users()
    if not users:
        st.warning("⚠️ 尚無帳號資料")
        return

    df = pd.DataFrame(users)

    df = df.rename(columns={
        "id": "ID",
        "username": "帳號",
        "is_admin": "管理員",
        "company_name": "公司",
        "is_active": "啟用中",
        "note": "備註",
    })
    df["備註"] = df["備註"].fillna("")
    df["公司"] = df["公司"].fillna("")

    search = st.text_input("🔍 搜尋帳號、公司或備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 匯出 CSV
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="📤 匯出帳號清單 (CSV)",
        data=csv_buffer.getvalue(),
        file_name="帳號清單.csv",
        mime="text/csv",
    )

    # AgGrid 設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("啟用中", editable=True)
    gb.configure_column("管理員", editable=True)
    gb.configure_selection("multiple", use_checkbox=True)  # ✅ 多筆選擇

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=450,
        theme="streamlit",
    )

    updated_df = grid["data"]
    selected = grid.get("selected_rows", [])

    if isinstance(selected, list) and len(selected) > 0:
        selected_ids = [row.get("ID") for row in selected]
        selected_usernames = [row.get("帳號", "") for row in selected]
        st.info(f"✏️ 已選取帳號：{'、'.join(selected_usernames)}")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 儲存變更"):
                updated_count = 0
                for row in selected:
                    user_id = row.get("ID")
                    payload = {
                        "note": row.get("備註", ""),
                        "active": row.get("啟用中", False),
                        "is_admin": row.get("管理員", False)
                    }
                    if update_user(user_id, payload):
                        updated_count += 1
                st.success(f"✅ 已更新 {updated_count} 筆資料")

        with col2:
            if st.button("🛑 停用帳號"):
                failed = []
                for row in selected:
                    if not update_user(row.get("ID"), {"active": False}):
                        failed.append(row.get("帳號"))
                if not failed:
                    st.success("✅ 所選帳號已全部停用")
                else:
                    st.warning(f"⚠️ 以下帳號停用失敗：{', '.join(failed)}")

        with col3:
            if st.button("🗑️ 刪除帳號"):
                failed = []
                for row in selected:
                    if not delete_user(row.get("ID")):
                        failed.append(row.get("帳號"))
                if not failed:
                    st.success("✅ 所選帳號已刪除")
                else:
                    st.warning(f"⚠️ 以下帳號刪除失敗：{', '.join(failed)}")

        # 只有選到 1 筆時才允許修改密碼
        if len(selected) == 1:
            st.markdown("---")
            st.subheader("🔐 修改密碼")
            new_pw = st.text_input("請輸入新密碼", type="password", key="pw_input")
            if st.button("🚀 修改密碼"):
                if new_pw.strip() == "":
                    st.warning("請輸入新密碼")
                else:
                    if update_password(selected[0].get("ID"), new_pw.strip()):
                        st.success("✅ 密碼已成功修改")
                    else:
                        st.error("❌ 密碼修改失敗")
    else:
        st.info("👈 請選擇至少一筆帳號進行操作")

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
