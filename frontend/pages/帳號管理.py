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
    df["動作"] = "無操作"

    search = st.text_input("🔍 搜尋帳號／公司／備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📤 匯出帳號清單 (CSV)", data=csv, file_name="帳號清單.csv", mime="text/csv")

    # ======================
    # 表格設定與顯示
    # ======================
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, resizable=True, wrapText=True, autoHeight=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column("啟用中", editable=True)
    gb.configure_column("管理員", editable=True)

    # 動作欄：設定為下拉選單
    gb.configure_column(
        "動作",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": ["無操作", "停用帳號", "刪除帳號"]}
    )

    gb.configure_selection("multiple", use_checkbox=True)

    st.markdown("### 👥 帳號清單")
    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        theme="streamlit",
        height=380,
        allow_unsafe_jscode=True,
    )

    selected = grid.get("selected_rows", [])
    updated_df = grid["data"]

    # ✅ 修正錯誤條件判斷（只改這行）
    if selected is not None and isinstance(selected, list) and len(selected) == 1:
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

    # ======================
    # 帳號操作按鈕（下移）
    # ======================
    st.markdown("---")
    st.subheader("🛠️ 帳號操作")

    if st.button("💾 儲存變更"):
        if not updated_df.empty:
            count_update, count_disable, count_delete = 0, 0, 0
            for _, row in updated_df.iterrows():
                user_id = row["ID"]
                note = row["備註"]
                is_active = row["啟用中"]
                is_admin = row["管理員"]
                action = row["動作"]

                # 一般更新
                update_user(user_id, {
                    "note": note,
                    "is_active": is_active,
                    "is_admin": is_admin,
                })
                count_update += 1

                # 動作處理
                if action == "停用帳號":
                    update_user(user_id, {"is_active": False})
                    count_disable += 1
                elif action == "刪除帳號":
                    delete_user(user_id)
                    count_delete += 1

            st.success(f"✅ 更新完成：{count_update} 筆更新，{count_disable} 筆停用，{count_delete} 筆刪除")

# 🌐 執行
def run():
    main()
