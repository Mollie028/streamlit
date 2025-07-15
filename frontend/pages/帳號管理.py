import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

API_URL = "https://ocr-whisper-production-2.up.railway.app"

# ---------------- API functions ----------------
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
        res = requests.put(f"{API_URL}/update_user_password/{user_id}", json={"password": new_password})
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

# ---------------- Main UI ----------------
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

    # 搜尋功能
    search = st.text_input("🔍 搜尋帳號／公司／備註")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 匯出功能
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📤 匯出帳號清單 (CSV)", data=csv, file_name="帳號清單.csv", mime="text/csv")

    # 標記要下拉選單的列（僅勾選的）
    selected_rows = []

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=False, resizable=True)

    # 使欄位平均分配寬度
    columns = ["ID", "帳號", "管理員", "公司", "啟用中", "備註"]
    for col in columns:
        gb.configure_column(col, width=120, flex=1)

    gb.configure_column("備註", editable=True)
    gb.configure_column("管理員", editable=True)
    gb.configure_column("公司", editable=True)

    gb.configure_selection("multiple", use_checkbox=True)

    st.markdown("### 👥 帳號清單")
    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=380,
        allow_unsafe_jscode=True,
        theme="streamlit",
    )

    selected = grid.get("selected_rows", [])
    updated_df = grid["data"]

    # ---------------- 密碼修改 ----------------
    if selected and len(selected) == 1:
        st.markdown("---")
        st.subheader("🔐 修改密碼")
        new_pw = st.text_input("請輸入新密碼", type="password")
        if st.button("🚀 修改密碼"):
            if new_pw.strip() == "":
                st.warning("請輸入新密碼")
            else:
                if update_password(selected[0]["ID"], new_pw.strip()):
                    st.success("✅ 密碼修改成功")
                else:
                    st.error("❌ 密碼修改失敗")

    # ---------------- 帳號操作區 ----------------
    st.markdown("---")
    st.subheader("🛠️ 帳號操作")

    if st.button("💾 儲存變更"):
        if updated_df.empty:
            st.warning("❌ 無可更新的內容")
            return

        updated_ids = [row["ID"] for row in selected]
        count_update, count_disable, count_enable, count_delete = 0, 0, 0, 0

        for _, row in updated_df.iterrows():
            user_id = row["ID"]
            if user_id not in updated_ids:
                continue  # 忽略沒被選取的

            current_status = row["啟用中"]
            note = row["備註"]
            is_admin = row["管理員"]
            company = row["公司"]

            # 下拉選單：處理帳號狀態
            action = None
            if current_status == "刪除帳號":
                if delete_user(user_id):
                    count_delete += 1
                continue
            elif current_status == "停用帳號":
                if update_user(user_id, {"is_active": False}):
                    count_disable += 1
                continue
            elif current_status == "啟用帳號":
                if update_user(user_id, {"is_active": True}):
                    count_enable += 1
                continue

            # 其他欄位一般更新
            success = update_user(user_id, {
                "note": note,
                "is_admin": is_admin,
                "company_name": company,
            })
            if success:
                count_update += 1

        st.success(f"✅ 儲存完成：{count_update} 筆一般更新，{count_enable} 筆啟用，{count_disable} 筆停用，{count_delete} 筆刪除")

# 執行
def run():
    main()
