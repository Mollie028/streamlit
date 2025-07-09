import streamlit as st
import requests
from core.config import API_BASE

def run():
    st.title("👑 使用者管理功能")

    # 📡 從後端取得使用者列表
    try:
        res = requests.get(f"{API_BASE}/get_users")
        if res.status_code != 200:
            st.error("❌ 無法取得使用者列表")
            return
        users = res.json()
    except Exception as e:
        st.error(f"❌ 取得使用者資料時發生錯誤：{str(e)}")
        return

    # -------------------------
    # 🔑 修改使用者密碼區塊
    # -------------------------
    st.subheader("🔑 更新使用者密碼")
    selected_user = st.selectbox("選擇帳號", [u["username"] for u in users], key="password_user")
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

    st.markdown("---")

    # -------------------------
    # 👥 修改使用者身分（權限）
    # -------------------------
    st.subheader("🛠️ 修改使用者權限")
    selected_role_user = st.selectbox("選擇帳號", [u["username"] for u in users], key="role_user")

    current_user = next((u for u in users if u["username"] == selected_role_user), None)
    current_is_admin = current_user["is_admin"] if current_user else False

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

    # -------------------------
    # 🧾 美化版帳號清單（移到下方）
    # -------------------------
    st.markdown("---")
    st.subheader("📋 使用者帳號清單")

    for u in users:
        with st.expander(f"👤 {u['username']}"):
            st.markdown(f"""
            - 🆔 **ID**：{u['id']}
            - 🙍‍♂️ **帳號**：{u['username']}
            - 🛡️ **身份**：{"管理員" if u['is_admin'] else "一般使用者"}
            """)

    # 🔙 返回首頁
    st.markdown("---")
    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
