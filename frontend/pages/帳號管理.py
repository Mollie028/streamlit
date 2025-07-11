import streamlit as st
import requests
from core.config import API_BASE

st.subheader("👥 帳號管理")

# 顯示所有使用者列表
st.markdown("### 所有使用者帳號")
try:
    res = requests.get(
        f"{API_BASE}/users",
        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
    )
    if res.status_code == 200:
        users = res.json()
        if isinstance(users, list):
            for user in users:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"👤 {user['username']} ({'管理員' if user.get('is_admin') else '使用者'})")
                with col2:
                    if st.button(f"修改密碼 - {user['username']}", key=f"change_{user['id']}"):
                        st.session_state["change_password_username"] = user['username']
                with col3:
                    pass  # 未來可加上停權、刪除帳號等功能
        else:
            st.error("回傳資料格式錯誤，應為使用者清單")
    else:
        st.error("API 回傳錯誤，請確認權限與登入狀態")
except Exception as e:
    st.error("無法取得使用者清單")
    st.code(str(e))

# 修改密碼區塊
if "change_password_username" in st.session_state:
    username = st.session_state["change_password_username"]
    st.markdown("---")
    st.markdown(f"### 🔐 修改使用者「{username}」密碼")
    new_password = st.text_input("輸入新密碼", type="password")

    if st.button("確認修改"):
        try:
            res = requests.put(
                f"{API_BASE}/update_password",
                json={"username": username, "new_password": new_password},
                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
            )
            if res.status_code == 200:
                st.success("✅ 密碼已成功更新！")
                del st.session_state["change_password_username"]
                st.rerun()
            else:
                st.error(f"密碼修改失敗：{res.text}")
        except Exception as e:
            st.error("🚨 系統錯誤")
            st.code(str(e))

    if st.button("取消"):
        del st.session_state["change_password_username"]
        st.rerun()
