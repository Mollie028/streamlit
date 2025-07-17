import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼")

# 🔸 建立狀態選項下拉選單
def status_options(status):
    if status == "啟用中":
        return ["啟用中", "停用帳號", "刪除帳號"]
    elif status == "已停用":
        return ["已停用", "啟用帳號", "刪除帳號"]
    else:
        return [status]  # 保留未知狀態

# 🔸 處理回傳資料為 DataFrame
def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    # 顯示欄位名稱轉換
    rename_map = {
        "id": "使用者ID",
        "username": "帳號名稱",
        "company": "公司名稱",
        "is_admin": "是否為管理員",
        "status": "狀態",
        "note": "備註"
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # 補齊欄位
    for col in ["是否為管理員", "備註", "狀態"]:
        if col not in df.columns:
            df[col] = ""

    # 建立狀態選項欄位
    df["狀態選項"] = df["狀態"].apply(status_options)

    return df

# 🔸 主畫面
def main():
    st.title("👩‍💼 帳號清單")

    try:
        res = requests.get("https://ocr-whisper-production-2.up.railway.app/users")
        res.raise_for_status()
        users = res.json()
    except Exception as e:
        st.error(f"❌ 取得使用者資料失敗：{e}")
        return

    df = process_users(users)

    if df.empty:
        st.info("目前尚無使用者資料")
        return

    # AgGrid 設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_default_column(editable=True)

    if "狀態" in df.columns:
        gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor",
                            cellEditorParams={"values": ["啟用中", "停用帳號", "刪除帳號"]})
    if "備註" in df.columns:
        gb.configure_column("備註", editable=True)
    if "是否為管理員" in df.columns:
        gb.configure_column("是否為管理員", editable=True, cellEditor="agCheckboxCellEditor")

    gridOptions = gb.build()

    AgGrid(df, gridOptions=gridOptions, update_mode=GridUpdateMode.VALUE_CHANGED,
           fit_columns_on_grid_load=True, height=380, theme="streamlit")

    st.button("💾 儲存變更")
    st.button("⬅️ 返回主頁")

# ✅ 提供 app.py 呼叫
def run():
    main()
