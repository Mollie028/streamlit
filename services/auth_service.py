import streamlit as st
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from frontend.components.auth import is_admin_user
from frontend.components.nav import nav_page
from core.config import API_BASE

# 中文欄位名稱對照
COLUMN_RENAMES = {
    "id": "ID",
    "username": "使用者帳號",
    "is_admin": "是否為管理員",
    "is_active": "使用者狀況",
    "note": "備註"
}

STATUS_OPTIONS = ["啟用", "停用", "刪除"]

# 狀態與布林值轉換
status_to_bool = {"啟用": True, "停用": False, "刪除": "刪除"}
bool_to_status = {True: "啟用", False: "停用"}

# 🔁 取得所有使用者資料
def get_users():
    res = requests.get(f"{API_BASE}/users")
    if res.status_code == 200:
        return res.json()
    else:
        st.error("無法取得使用者資料")
        return []

# 💾 儲存變更（單筆）
def update_user(user):
    uid = user["id"]
    status_value = user["使用者狀況"]

    if status_value == "刪除":
        res = requests.delete(f"{API_BASE}/delete_user/{uid}")
    else:
        payload = {
            "note": user["備註"],
            "is_admin": user["是否為管理員"],
            "is_active": status_to_bool[status_value]
        }
        res = requests.put(f"{API_BASE}/update_user/{uid}", json=payload)
    return res.status_code

# 🔐 權限檢查 + 主邏輯

def run():
    st.title("帳號管理 👥")

    # 返回鍵
    if st.button("← 返回首頁"):
        nav_page("首頁")

    if not is_admin_user():
        st.warning("⛔️ 僅限管理員使用")
        return

    # 載入資料
    users = get_users()
    if not users:
        return

    # 欄位轉換與整理
    for u in users:
        u["使用者帳號"] = u.pop("username")
        u["是否為管理員"] = u.pop("is_admin")
        u["使用者狀況"] = bool_to_status.get(u.pop("is_active"), "啟用")
        u["備註"] = u.get("note", "")

    gb = GridOptionsBuilder.from_dataframe(
        pd.DataFrame(users)[list(COLUMN_RENAMES.values())]
    )
    gb.configure_default_column(editable=False, resizable=True)
    gb.configure_column("是否為管理員", editable=True)
    gb.configure_column("備註", editable=True)
    gb.configure_column(
        "使用者狀況",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": STATUS_OPTIONS},
    )
    gb.configure_grid_options(domLayout='normal')

    grid_response = AgGrid(
        pd.DataFrame(users)[list(COLUMN_RENAMES.values())],
        gridOptions=gb.build(),
        height=380,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True
    )

    updated_rows = grid_response["data"]

    if st.button("💾 儲存變更"):
        success = True
        for row in updated_rows.to_dict(orient="records"):
            code = update_user(row)
            if code != 200:
                success = False
        if success:
            st.success("✅ 所有變更已儲存！請重新登入以查看更新。")
        else:
            st.error("⚠️ 有些變更未成功，請稍後再試或檢查資料。")
