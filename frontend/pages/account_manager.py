import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼")

st.title("👩‍💼 帳號清單")

st.markdown("---")

# 🚨 輔助函式：狀態下拉選單
def status_options(status):
    if status == "啟用中":
        return ["停用帳號", "刪除帳號"]
    else:
        return ["啟用帳號", "刪除帳號"]

# ✅ 輔助函式：處理使用者資料
def process_users(users):
    if not isinstance(users, list):
        st.error("回傳資料格式錯誤")
        return pd.DataFrame()
    if len(users) == 0:
        st.warning("尚無有效使用者資料，請稍後再試。")
        return pd.DataFrame()

    df = pd.DataFrame(users)

    # ✅ 安全處理缺少欄位
    if "公司名稱" not in df.columns:
        df["公司名稱"] = "GSLD"
    if "狀態" not in df.columns:
        df["狀態"] = "啟用中"

    # ✅ 加上狀態選項欄位
    df["狀態選項"] = df["狀態"].apply(status_options)

    return df

# ✅ 呼叫 API
try:
    res = requests.get("https://ocr-whisper-production-2.up.railway.app/users")
    users = res.json()
    df = process_users(users)

    if not df.empty:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(editable=True)
        gb.configure_column("狀態", editable=True, cellEditor="agSelectCellEditor",
                            cellEditorParams={"values": ["啟用中", "停用帳號", "刪除帳號"]})
        gb.configure_column("備註", editable=True)

        gridOptions = gb.build()
        AgGrid(df, gridOptions=gridOptions, update_mode=GridUpdateMode.VALUE_CHANGED)

        st.button("💾 儲存變更")
except Exception as e:
    st.error(f"讀取使用者資料失敗：{e}")

st.markdown("---")
st.button("⬅️ 返回主頁")
