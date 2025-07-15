import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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

    # ======================
    # 替換啟用欄為動作欄（如果選取）
    # ======================
    if selected:
        selected_ids = [s["ID"] for s in selected]
        for idx, row in updated_df.iterrows():
            if row["ID"] in selected_ids:
                if row["啟用中"]:
                    updated_df.at[idx, "啟用中"] = "停用帳號"
                else:
                    updated_df.at[idx, "啟用中"] = "啟用帳號"

    # ======================
    # 修改密碼
    # ======================
    if selected and len(selected) == 1:
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
            count_update, count_disable, count_enable, count_delete = 0, 0, 0, 0
            for _, row in updated_df.iterrows():
                user_id = row["ID"]
                note = row["備註"]
                is_admin = row["管理員"]
                status = row["啟用中"]

                # 狀態處理邏輯
                if status == True or status == "啟用帳號":
                    is_active = True
                elif status == "停用帳號":
                    is_active = False
                elif status == "刪除帳號":
                    if delete_user(user_id):
                        count_delete += 1
                    continue
                else:
                    continue

                # 更新帳號資訊
                if update_user(user_id, {
                    "note": note,
                    "is_active": is_active,
                    "is_admin": is_admin,
                }):
                    count_update += 1
                    if not is_active:
                        count_disable += 1
                    else:
                        count_enable += 1

            st.success(f"✅ 完成：{count_update} 筆更新（啟用 {count_enable} 筆，停用 {count_disable} 筆），刪除 {count_delete} 筆")

def run():
    main()
