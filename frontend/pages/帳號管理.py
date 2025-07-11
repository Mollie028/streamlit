import streamlit as st
import requests
import pandas as pd
from core.config import API_BASE

def run():
    st.subheader("👥 帳號管理")

    try:
        res = requests.get(
            f"{API_BASE}/users",
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        if res.status_code == 200:
            users = res.json()
            if isinstance(users, list):
                df = pd.DataFrame(users)

                # ✅ 顯示中文欄位名稱
                df_display = df.rename(columns={
                    "id": "使用者編號",
                    "username": "使用者帳號",
                    "is_admin": "是否為管理員",
                    "company_name": "公司名稱",
                    "note": "備註說明",
                    "is_active": "帳號狀態"
                })

                # ✅ 欄位轉換顯示
                df_display["是否為管理員"] = df_display["是否為管理員"].apply(lambda x: "✅ 是" if x else "❌ 否")
                df_display["帳號狀態"] = df_display["帳號狀態"].apply(lambda x: "🟢 啟用中" if x else "⛔ 停用")

                st.markdown("### 所有使用者帳號")
                st.dataframe(df_display, use_container_width=True)

                st.markdown("---")
                st.markdown("### 🔐 修改使用者密碼")

                # ✅ 動態密碼欄位與送出按鈕
                for user in users:
                    st.markdown(f"#### 👤 {user['username']}（{'管理員' if user['is_admin'] else '使用者'}）")
                    new_pw = st.text_input(
                        f"請輸入新密碼 - {user['username']}",
                        type="password",
                        key=f"pw_input_{user['id']}"
                    )
                    if st.button(f"✅ 確認修改密碼 - {user['username']}", key=f"submit_{user['id']}"):
                        try:
                            pw_res = requests.put(
                                f"{API_BASE}/update_password",
                                json={"username": user['username'], "new_password": new_pw},
                                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                            )
                            if pw_res.status_code == 200:
                                st.success(f"✅ 已成功修改 {user['username']} 的密碼")
                            else:
                                st.error(f"❌ 修改失敗：{pw_res.json().get('detail', '未知錯誤')}")
                        except Exception as e:
                            st.error("🚨 系統錯誤")
                            st.code(str(e))
                        st.rerun()
            else:
                st.error("⚠️ 回傳資料格式錯誤")
        else:
            st.error("⚠️ 無法取得使用者清單，請確認權限或登入狀態")
    except Exception as e:
        st.error("🚨 系統錯誤，請稍後再試")
        st.code(str(e))

    st.markdown("---")
    if st.button("🔙 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
