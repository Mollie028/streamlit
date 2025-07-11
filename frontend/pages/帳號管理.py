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
                df = pd.DataFrame(users)
                df = df.rename(columns={
                    "id": "使用者編號",
                    "username": "使用者帳號",
                    "is_admin": "是否為管理員",
                    "company_name": "公司名稱",
                    "note": "備註說明",
                    "is_active": "帳號狀態"
                })
                df["是否為管理員"] = df["是否為管理員"].apply(lambda x: "✅ 是" if x else "❌ 否")
                df["帳號狀態"] = df["帳號狀態"].apply(lambda x: "🟢 啟用中" if x else "⛔ 停用")

                st.dataframe(df.head(5), use_container_width=True)

                st.markdown("---")
                st.markdown("### 🔍 搜尋並編輯使用者帳號")

                search_term = st.text_input("請輸入帳號或 ID 以搜尋使用者")
                matched_users = [u for u in users if search_term and (search_term.lower() in u['username'].lower() or str(u['id']) == search_term)]

                if matched_users:
                    user = matched_users[0]
                    st.markdown(f"#### 🧑‍💻 目前選取帳號：**{user['username']}**（{'管理員' if user['is_admin'] else '使用者'}）")

                    # 修改密碼
                    st.markdown("##### 🔐 修改密碼")
                    new_password = st.text_input("請輸入新密碼", type="password", key="pwd_input")
                    if st.button("✅ 確認修改密碼"):
                        try:
                            res = requests.put(
                                f"{API_BASE}/update_password",
                                json={"username": user['username'], "new_password": new_password},
                                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                            )
                            if res.status_code == 200:
                                st.success("密碼已成功更新 ✅")
                            else:
                                st.error("密碼更新失敗 ❌")
                        except Exception as e:
                            st.error("🚨 系統錯誤")
                            st.code(str(e))

                    st.markdown("##### 🚫 停用 / 啟用帳號")
                    current_status = "啟用中" if user['is_active'] else "已停用"
                    st.write(f"目前狀態：**{current_status}**")

                    toggle_label = "停用帳號" if user['is_active'] else "啟用帳號"
                    if st.button(f"{toggle_label}"):
                        try:
                            res = requests.put(
                                f"{API_BASE}/toggle_active",
                                json={"user_id": user['id']},
                                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                            )
                            if res.status_code == 200:
                                st.success("帳號狀態已更新 ✅")
                                st.rerun()
                            else:
                                st.error("狀態更新失敗 ❌")
                        except Exception as e:
                            st.error("🚨 系統錯誤")
                            st.code(str(e))

                elif search_term:
                    st.warning("查無符合的使用者帳號")

            else:
                st.error("⚠️ 回傳資料格式錯誤")
        else:
            st.error("⚠️ 無法取得使用者清單，請確認權限或登入狀態")
    except Exception as e:
        st.error("🚨 系統錯誤，請稍後再試")
        st.code(str(e))
