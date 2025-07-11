import streamlit as st
import requests
import pandas as pd
from core.config import API_BASE

def run():
    st.subheader("👥 帳號管理")
    st.markdown("### 所有使用者帳號")

    try:
        res = requests.get(
            f"{API_BASE}/users",
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        if res.status_code == 200:
            users = res.json()
            if isinstance(users, list):
                # ✅ 改欄位名稱為中文 + 狀態文字化
                df = pd.DataFrame(users)
                df = df.rename(columns={
                    "id": "使用者編號",
                    "username": "使用者帳號",
                    "is_admin": "是否為管理員",
                    "note": "備註說明",
                    "is_active": "帳號狀態"
                })
                df["是否為管理員"] = df["是否為管理員"].apply(lambda x: "✅ 是" if x else "❌ 否")
                df["帳號狀態"] = df["帳號狀態"].apply(lambda x: "🟢 啟用中" if x else "⛔ 停用")

                st.dataframe(df, use_container_width=True)

                # ✅ 修改密碼按鈕列表
                st.markdown("---")
                st.markdown("### 🔐 修改使用者密碼")
                for user in users:
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown(f"👤 **{user['username']}**（{'管理員' if user['is_admin'] else '使用者'}）")
                    with col2:
                        if st.button(f"修改密碼 - {user['username']}", key=f"btn_{user['id']}"):
                            st.session_state["change_password_username"] = user["username"]
                            st.rerun()
            else:
                st.error("⚠️ 回傳資料格式錯誤")
        else:
            st.error("⚠️ 無法取得使用者清單，請確認權限或登入狀態")
    except Exception as e:
        st.error("🚨 系統錯誤，請稍後再試")
        st.code(str(e))

    # ✅ 顯示修改密碼表單區塊
    if "change_password_username" in st.session_state:
        username = st.session_state["change_password_username"]
        st.markdown("---")
        st.markdown(f"#### 🛠️ 修改帳號 **{username}** 的密碼")
        new_password = st.text_input("請輸入新密碼", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 確認修改"):
                try:
                    res = requests.put(
                        f"{API_BASE}/update_password",
                        json={"username": username, "new_password": new_password},
                        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                    )
                    if res.status_code == 200:
                        st.success("密碼已成功更新 ✅")
                        del st.session_state["change_password_username"]
                        st.rerun()
                    else:
                        st.error("❌ 密碼更新失敗，請稍後再試")
                except Exception as e:
                    st.error("🚨 系統錯誤")
                    st.code(str(e))
        with col2:
            if st.button("取消修改"):
                del st.session_state["change_password_username"]
                st.rerun()

    # ✅ 返回首頁按鈕
    st.markdown("---")
    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
