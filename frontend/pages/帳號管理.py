import streamlit as st
import requests
from core.config import API_BASE

def run():
    st.title("🗂️ 帳號管理（管理員專用）")

    # 取得所有帳號
    try:
        res = requests.get(f"{API_BASE}/get_users")
        if res.status_code == 200:
            users = res.json()
        else:
            st.error("❌ 無法取得使用者清單")
            return
    except Exception as e:
        st.error("❌ 發生錯誤")
        st.code(str(e))
        return

    # 顯示帳號清單
    st.subheader("👥 使用者帳號列表")
    st.table(users)

    # 密碼更新區塊
    st.subheader("🔑 更新使用者密碼")
    selected_user = st.selectbox("選擇帳號", [u["username"] for u in users])
    new_pass = st.text_input("輸入新密碼", type="password")

    if st.button("更新密碼"):
        if not new_pass:
            st.warning("⚠️ 密碼不可為空")
        else:
            try:
                res = requests.put(
                    f"{API_BASE}/update_password",
                    params={"username": selected_user, "new_password": new_pass}
                )
                if res.status_code == 200:
                    st.success("✅ 密碼更新成功")
                else:
                    st.error(f"❌ 更新失敗：{res.text}")
            except Exception as e:
                st.error("❌ 更新錯誤")
                st.code(str(e))
