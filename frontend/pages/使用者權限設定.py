import streamlit as st
import requests
import pandas as pd
from core.config import API_BASE

def render():
    st.set_page_config(page_title="使用者權限設定", page_icon="👥")
    st.title("👥 使用者權限設定（管理員專用）")

    # 取得所有使用者帳號
    try:
        res = requests.get(f"{API_BASE}/get_users")
        if res.status_code == 200:
            users = res.json()
            df = pd.DataFrame(users)
            st.subheader("📋 使用者列表")
            st.dataframe(df[["id", "username", "is_admin"]], use_container_width=True)
        else:
            st.error("❌ 無法取得使用者列表")
            return
    except Exception as e:
        st.error(f"❌ 系統錯誤：{str(e)}")
        return

    st.divider()
    st.subheader("🛠️ 調整使用者身份權限")

    usernames = [u["username"] for u in users]
    selected_user = st.selectbox("選擇使用者帳號", usernames)

    # 找出該使用者目前的權限
    current_status = next((u["is_admin"] for u in users if u["username"] == selected_user), False)
    new_status = st.radio("設定使用者身分", ["使用者", "管理員"], index=1 if current_status else 0, horizontal=True)

    if st.button("✅ 更新使用者權限"):
        payload = {
            "username": selected_user,
            "is_admin": new_status == "管理員"
        }
        try:
            res = requests.post(f"{API_BASE}/update_role", json=payload)
            if res.status_code == 200:
                st.success("✅ 使用者權限已更新")
                st.rerun()
            else:
                st.error("❌ 更新失敗")
        except Exception as e:
            st.error(f"❌ 系統錯誤：{str(e)}")

    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
