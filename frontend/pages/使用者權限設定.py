import streamlit as st
import requests
from core.config import API_BASE

def run():
    st.title("👑 使用者管理功能（管理員專用）")

    # 🧾 取得所有使用者
    try:
        res = requests.get(f"{API_BASE}/get_users")
        if res.status_code != 200:
            st.error("❌ 無法取得使用者列表")
            return
        users = res.json()
    except Exception as e:
        st.error(f"❌ 取得使用者資料時發生錯誤：{str(e)}")
        return

    # 取得目前登入者資訊與公司名稱
    current_username = st.session_state.get("username", "")
    current_user = next((u for u in users if u["username"] == current_username), None)

    if not current_user:
        st.error("❌ 無法找到當前使用者資訊")
        return

    current_company = current_user.get("company_name", "")
    same_company_users = [u for u in users if u.get("company_name") == current_company]

    # -------------------------
    # 🛠️ 修改使用者權限（只顯示同公司）
    # -------------------------
    st.subheader("🛠️ 修改使用者權限")
    usernames = [u["username"] for u in same_company_users]
    selected_role_user = st.selectbox("選擇帳號", usernames, key="role_user")

    selected_user_obj = next((u for u in same_company_users if u["username"] == selected_role_user), None)
    current_is_admin = selected_user_obj["is_admin"] if selected_user_obj else False

    new_is_admin = st.radio("設定身分", ["一般使用者", "管理員"], index=1 if current_is_admin else 0)
    is_admin_value = (new_is_admin == "管理員")

    if st.button("✅ 更新使用者權限"):
        payload = {
            "username": selected_role_user,
            "is_admin": is_admin_value
        }
        try:
            res = requests.post(f"{API_BASE}/update_role", json=payload)
            if res.status_code == 200:
                st.success("✅ 使用者權限更新成功")
                st.rerun()
            else:
                st.error(f"❌ 更新失敗：{res.text}")
        except Exception as e:
            st.error(f"❌ 系統錯誤：{str(e)}")

    st.markdown("---")

    # -------------------------
    # 📋 表格：同公司使用者清單
    # -------------------------
    st.subheader("📋 使用者帳號列表（僅顯示同公司）")

    table_data = [
        {
            "ID": u["id"],
            "帳號": u["username"],
            "公司": u.get("company_name", "未提供"),
            "身份": "管理員" if u["is_admin"] else "一般使用者"
        }
        for u in same_company_users
    ]

    st.table(table_data)  # ✅ 用表格呈現

    st.markdown("---")
    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
