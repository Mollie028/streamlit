import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

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
# 主畫面 UI
# ---------------------------
def main():
    st.title("👤 帳號管理面板")

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
    df["動作"] = "無操作"  # 新增欄位

    # 🔍 搜尋
    search = st.text_input("🔍 搜尋帳號／公司／備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 📤 匯出 CSV
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📤 匯出帳號清單 (CSV)", data=csv, file_name="帳號清單.csv", mime="text/csv")

    # 👉 AgGrid 表格設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, resizable=True, wrapText=True, autoHeight=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("啟用中", editable=True)
    gb.configure_column("管理員", editable=True)

    # 設定下拉選單選項
    action_options = ["無操作", "停用帳號", "刪除帳號"]
    gb.configure_column(
        "動作",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": action_options},
    )

    gb.configure_selection("multiple", use_checkbox=True)

    with st.container():
        st.markdown('<div style="max-width: 1000px;">', unsafe_allow_html=True)

        grid = AgGrid(
            df,
            gridOptions=gb.build(),
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            theme="streamlit",
            height=380,
        )

        selected = grid.get("selected_rows", [])
        updated_df = grid["data"]

        st.markdown("</div>", unsafe_allow_html=True)

    # 🔐 修改密碼區塊（只選取一筆帳號才出現）
    if len(selected) == 1:
        st.markdown("---")
        st.subheader("🔐 修改密碼")
        new_pw = st.text_input("請輸入新密碼", type="password", key="pw_input")
        if st.button("🚀 修改密碼"):
            if new_pw.strip() == "":
                st.warning("請輸入新密碼")
            else:
                if update_password(selected[0]["ID"], new_pw.strip()):
                    st.success("✅ 密碼修改成功")
                else:
                    st.error("❌ 密碼修改失敗")

    # 💾 儲存變更按鈕（如果有修改密碼，就放在下面）
    st.markdown("---")
    st.subheader("🛠️ 儲存變更")
    if st.button("💾 儲存變更"):
        if not selected:
            st.warning("請選取要儲存的帳號")
        else:
            count = 0
            for row in selected:
                user_id = row["ID"]

                # 更新基本資料
                update_user(user_id, {
                    "note": row["備註"],
                    "is_active": row["啟用中"],
                    "is_admin": row["管理員"],
                })

                # 執行動作
                action = row.get("動作", "無操作")
                if action == "停用帳號":
                    update_user(user_id, {"is_active": False})
                elif action == "刪除帳號":
                    delete_user(user_id)

                count += 1
            st.success(f"✅ 完成 {count} 筆帳號的更新與操作")

# 🌐 執行
def run():
    main()
