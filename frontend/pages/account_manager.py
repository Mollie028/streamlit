import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="帳號管理", layout="wide")

API_BASE = "https://ocr-whisper-production-2.up.railway.app"

def run():
    st.markdown("## 👤 帳號管理")

    # 使用者資料請求
    try:
        res = requests.get(f"{API_BASE}/users")
        users = res.json()
    except Exception as e:
        st.error(f"無法取得使用者資料：{e}")
        return

    df = pd.DataFrame(users)
    if df.empty:
        st.info("尚無使用者資料")
        return

    # 表格欄位轉換
    df["啟用狀態"] = df["is_active"].apply(lambda x: "啟用中" if x else "已停用")
    df["是否為管理員"] = df["is_admin"].apply(lambda x: "✅" if x else "")

    show_df = df[["id", "username", "是否為管理員", "啟用狀態", "note"]]
    show_df.columns = ["使用者ID", "帳號名稱", "是否為管理員", "啟用狀態", "備註"]

    st.markdown("### 📋 使用者清單")
    gb = GridOptionsBuilder.from_dataframe(show_df)
    gb.configure_selection("single", use_checkbox=True)
    gb.configure_grid_options(domLayout="normal")
    grid_options = gb.build()

    grid_response = AgGrid(
        show_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=450,
        fit_columns_on_grid_load=True,
    )

    selected_rows = grid_response["selected_rows"]
    if selected_rows:
        selected = selected_rows[0]
        user_id = selected["使用者ID"]
        username = selected["帳號名稱"]
        is_active = selected["啟用狀態"] == "啟用中"

        st.markdown("### 🛠️ 帳號操作")
        st.write(f"👤 帳號：`{username}`")
        st.write(f"🆔 ID：`{user_id}`")
        st.write(f"🔒 狀態：{'啟用中' if is_active else '已停用'}")

        operation = st.selectbox("請選擇操作", ["停用帳號", "啟用帳號", "刪除帳號"] if is_active else ["啟用帳號", "刪除帳號"])
        if st.button("✅ 執行操作"):
            try:
                if operation == "停用帳號":
                    res = requests.put(f"{API_BASE}/disable_user/{user_id}")
                elif operation == "啟用帳號":
                    res = requests.put(f"{API_BASE}/enable_user/{user_id}")
                elif operation == "刪除帳號":
                    res = requests.delete(f"{API_BASE}/delete_user/{user_id}")
                else:
                    st.warning("未選擇任何操作")
                    return

                if res.status_code == 200:
                    st.success("✅ 操作成功")
                    st.rerun()
                else:
                    st.error(f"❌ 操作失敗：{res.text}")
            except Exception as e:
                st.error(f"執行錯誤：{e}")

if __name__ == "__main__":
    run()
