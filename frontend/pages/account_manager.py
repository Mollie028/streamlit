import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="帳號清單", page_icon="👩‍💼")

API_URL = "https://ocr-whisper-production-2.up.railway.app"

def status_options(status):
    if status == "啟用中":
        return ["啟用中", "停用帳號", "刪除帳號"]
    elif status == "已停用":
        return ["已停用", "啟用帳號", "刪除帳號"]
    else:
        return [status]

def process_users(users):
    df = pd.DataFrame(users)
    if df.empty:
        return df

    rename_map = {
        "id": "使用者ID",
        "username": "帳號名稱",
        "company": "公司名稱",
        "is_admin": "是否為管理員",
        "status": "狀態",
        "note": "備註"
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    for col in ["是否為管理員", "備註", "狀態"]:
        if col not in df.columns:
            df[col] = ""

    df["狀態選項"] = df["狀態"].apply(status_options)

    return df

def update_users(changes):
    for row in changes:
        user_id = row.get("使用者ID")
        status = row.get("狀態")
        note = row.get("備註", "")
        is_admin = row.get("是否為管理員", False)

        try:
            if status == "刪除帳號":
                requests.delete(f"{API_URL}/delete_user/{user_id}")
            elif status == "停用帳號":
                requests.put(f"{API_URL}/disable_user/{user_id}")
            elif status == "啟用帳號":
                requests.put(f"{API_URL}/enable_user/{user_id}")
            else:
                # 備註與管理員權限更新
                payload = {"note": note, "is_admin": is_admin}
                requests.put(f"{API_URL}/update_user/{user_id}", json=payload)
        except Exception as e:
            st.warning(f"⚠️ 更新帳號 {user_id} 失敗：{e}")

def main():
    st.title("👩‍💼 帳號清單")

    try:
        res = requests.get(f"{API_URL}/users")
        res.raise_for_status()
        users = res.json()
    except Exception as e:
        st.error(f"❌ 取得使用者資料失敗：{e}")
        return

    df = process_users(users)

    if df.empty:
        st.info("目前尚無使用者資料")
        return

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

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MANUAL,
        fit_columns_on_grid_load=True,
        height=380,
        theme="streamlit",
        allow_unsafe_jscode=True
    )

    # 🔸 實際儲存變更
    if st.button("💾 儲存變更"):
        updated_data = grid_response["data"]
        update_users(updated_data.to_dict("records"))
        st.success("✅ 變更已儲存")

    if st.button("⬅️ 返回主頁"):
        st.switch_page("首頁.py")

# 讓 app.py 可呼叫
def run():
    main()
