import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼")

REQUIRED_COLUMNS = ["status", "company"]

# 狀態選單
def status_options(status):
    if status == "啟用中":
        return ["停用帳號", "刪除帳號"]
    else:
        return ["啟用帳號", "刪除帳號"]

# 處理資料
def process_users(users):
    if not isinstance(users, list):
        st.error("❌ 後端回傳格式錯誤")
        return pd.DataFrame()

    if not users:
        st.warning("⚠️ 尚無有效使用者資料，請稍後再試。")
        return pd.DataFrame()

    df = pd.DataFrame(users)

    # 檢查是否缺欄位
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        st.error(f"⚠️ 回傳資料缺少欄位：{', '.join(missing_columns)}")
        return pd.DataFrame()

    # 加上狀態下拉選單欄位
    df["狀態選項"] = df["status"].apply(status_options)
    return df

def main():
    st.title("👩‍💼 帳號清單")
    st.markdown("")

    try:
        res = requests.get("https://ocr-whisper-production-2.up.railway.app/users")
        users = res.json()
        df = process_users(users)

        if df.empty:
            return

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(editable=True)

        # 下拉選單欄位
        gb.configure_column("status", editable=True, cellEditor="agSelectCellEditor",
                            cellEditorParams={"values": ["啟用中", "停用帳號", "刪除帳號"]})
        gb.configure_column("note", editable=True)  # 備註欄可編輯

        gridOptions = gb.build()
        AgGrid(df, gridOptions=gridOptions, update_mode=GridUpdateMode.VALUE_CHANGED)

        st.button("💾 儲存變更")

    except Exception as e:
        st.error(f"❌ 資料載入失敗：{e}")

    st.markdown("")
    st.button("⬅️ 返回主頁")

# ✅ 提供 app.py 呼叫
def run():
    main()
