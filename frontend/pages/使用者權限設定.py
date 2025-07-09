import streamlit as st
import requests
import pandas as pd
from core.config import API_BASE

def run():
    st.title("👑 使用者管理功能（管理員專用）")

    company = st.session_state.get("company_name", "")
    if not company:
        st.warning("⚠️ 未取得公司名稱，請重新登入")
        return

    # 📡 取得同公司使用者清單
    try:
        res = requests.get(f"{API_BASE}/get_users", params={"company_name": company})
        if res.status_code != 200:
            st.error("❌ 無法取得使用者資料")
            return
        users = res.json()
    except Exception as e:
        st.error(f"❌ 系統錯誤：{str(e)}")
        return

    usernames = [u["username"] for u in users]

    # ------------------------------------
    # 🛠️ 修改使用者權限
    # ------------------------------------
    st.subheader("🧰 修改使用者權限")
    selected_user = st.selectbox("選擇帳號", usernames, key="select_role")
    current_user = next((u for u in users if u["username"] == selected_user), None)
    current_is_admin = current_user["is_admin"] if current_user else False

    identity = st.radio("設定身分", ["一般使用者", "管理員"], index=1 if current_is_admin else 0)
    is_admin_value = identity == "管理員"

    if st.button("✅ 更新使用者權限"):
        try:
            payload = {"username": selected_user, "is_admin": is_admin_value}
            res = requests.post(f"{API_BASE}/update_role", json=payload)
            if res.status_code == 200:
                st.success("✅ 權限更新成功")
                st.rerun()
            else:
                st.error(f"❌ 更新失敗：{res.text}")
        except Exception as e:
            st.error(f"❌ 系統錯誤：{str(e)}")

    st.markdown("---")

    # ------------------------------------
    # 🔐 修改使用者密碼
    # ------------------------------------
    st.subheader("🔐 更新使用者密碼")
    selected_pass_user = st.selectbox("選擇帳號", usernames, key="select_pass")
    new_pass = st.text_input("輸入新密碼", type="password")

    if st.button("🔄 更新密碼"):
        if not new_pass:
            st.warning("⚠️ 密碼不可為空")
        else:
            try:
                res = requests.put(
                    f"{API_BASE}/update_password",
                    params={"username": selected_pass_user, "new_password": new_pass}
                )
                if res.status_code == 200:
                    st.success("✅ 密碼更新成功")
                else:
                    st.error(f"❌ 更新失敗：{res.text}")
            except Exception as e:
                st.error(f"❌ 系統錯誤：{str(e)}")

    st.markdown("---")

    # ------------------------------------
    # 📋 顯示使用者表格（只限同公司）
    # ------------------------------------
    st.subheader("📋 使用者帳號清單")
    same_company_users = [u for u in users if u.get("company_name") == company]

    if same_company_users:
        df = pd.DataFrame(same_company_users)
        df = df.rename(columns={
            "id": "ID",
            "username": "使用者名稱",
            "is_admin": "是否為管理員",
            "company_name": "公司名稱"
        })
        df["是否為管理員"] = df["是否為管理員"].apply(lambda x: "✅" if x else "❌")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("🔍 尚無其他同公司帳號")

    # 🔚 返回首頁
    st.markdown("---")
    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
