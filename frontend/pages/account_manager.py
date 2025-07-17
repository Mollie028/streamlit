import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.stylable_container import stylable_container

API_URL = "https://ocr-whisper-production-2.up.railway.app"

# 🧩 呼叫 API 拿帳號資料
def fetch_users():
    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"❌ 取得帳號資料失敗：{e}")
        return []

# 🧩 資料轉換成 DataFrame 並加上「狀態選項」
def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    # 欄位名稱轉換
    df = df.rename(columns={
        "id": "使用者ID",
        "username": "帳號名稱",
        "company": "公司名稱",
        "is_admin": "是否為管理員",
        "is_active": "啟用中",
        "note": "備註"
    })

    # 加上狀態欄位與下拉選單選項
    def compute_status(row):
        return "啟用中" if row["啟用中"] else "已停用"

    def get_status_options(status):
        return ["停用帳號", "刪除帳號"] if status == "啟用中" else ["啟用帳號", "刪除帳號"]

    df["狀態"] = df.apply(compute_status, axis=1)
    df["狀態選項"] = df["狀態"].apply(get_status_options)

    return df

# 🧩 將修改後的帳號資料送出
def update_users(changes):
    success_count = 0
    for row in changes:
        uid = row.get("使用者ID")
        status = row.get("狀態")
        note = row.get("備註")
        is_admin = row.get("是否為管理員")

        try:
            if status == "停用帳號":
                requests.put(f"{API_URL}/disable_user/{uid}")
            elif status == "啟用帳號":
                requests.put(f"{API_URL}/enable_user/{uid}")
            elif status == "刪除帳號":
                requests.delete(f"{API_URL}/delete_user/{uid}")
            else:
                payload = {"note": note, "is_admin": is_admin}
                requests.put(f"{API_URL}/update_user/{uid}", json=payload)
            success_count += 1
        except Exception as e:
            st.error(f"❌ 更新使用者 {uid} 時發生錯誤：{e}")

    if success_count:
        st.success(f"✅ 已成功儲存 {success_count} 筆變更！")

# ✅ 主函式：整個畫面都放這裡
def run():
    st.markdown("## 👩‍💼 帳號清單")

    users = fetch_users()
    df = process_users(users)

    if df.empty:
        st.warning("⚠️ 尚無有效使用者資料，請稍後再試。")
        return

    # ✅ AgGrid 設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")
    gb.configure_column("備註", editable=True)
    gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": []})
    gb.configure_column("狀態選項", hide=True)

    gridOptions = gb.build()

    # ✅ 手動設定每列的「狀態選項」作為 cellEditor 下拉值
    for col in gridOptions["columnDefs"]:
        if col["field"] == "狀態":
            col["cellEditorParams"] = {
                "function": "params => ({ values: params.data['狀態選項'] || [] })"
            }

    # ✅ 顯示表格
    grid_return = AgGrid(
        df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        theme="streamlit",
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=True,
        height=450,
    )

    # ✅ 儲存變更按鈕
    with stylable_container("save-btn", css_styles="button {margin-top: 1rem;}"):
        if st.button("💾 儲存變更"):
            updated = grid_return["data"]
            update_users(updated.to_dict("records"))
            st.experimental_rerun()

    # ✅ 返回主頁
    with stylable_container("back-btn", css_styles="button {margin-top: 1rem;}"):
        if st.button("🔙 返回主頁"):
            st.session_state["current_page"] = "home"
            st.rerun()
