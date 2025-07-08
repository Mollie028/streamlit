import streamlit as st
import requests
from core.config import API_BASE

def run():
    st.title("👥 使用者權限設定（僅限管理員）")

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

    # 🧾 顯示表格
    st.subheader("使用者清單")
    st.dataframe(users)

    # 🧑‍🔧 權限設定表單
    st.subheader("🔧 修改使用者權限")
    usernames = [u["username"] for u in users]
    selected_username = st.selectbox("選擇帳號", usernames)

    # 找到目前該使用者的 is_admin 狀態
    current_user = next((u for u in users if u["username"] == selected_username), None)
    current_is_admin = current_user["is_admin"] if current_user else False

    new_is_admin = st.radio("設定身分", ["一般使用者", "管理員"], index=1 if current_is_admin else 0)
    is_admin_value = (new_is_admin == "管理員")

    if st.button("✅ 更新使用者權限"):
        payload = {
            "username": selected_username,
            "is_admin": is_admin_value
        }

        try:
            res = requests.post(f"{API_BASE}/update_role", json=payload)
            if res.status_code == 200:
                st.success("✅ 使用者權限更新成功")
                st.rerun()  # 重新載入資料
            else:
                st.error(f"❌ 更新失敗：{res.text}")
        except Exception as e:
            st.error(f"❌ 系統錯誤：{str(e)}")

    # 🔙 返回首頁按鈕
    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
