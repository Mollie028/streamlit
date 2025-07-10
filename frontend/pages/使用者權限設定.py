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

    # 📱 取得同公司使用者清單
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
    # 🔨 修改使用者權限
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
    # 📋 顯示使用者帳號清單（含搜尋 + 分頁）
    # ------------------------------------
    st.subheader("📋 使用者帳號清單")

    same_company_users = [u for u in users if u.get("company_name") == company]

    search = st.text_input("🔍 搜尋使用者（可輸入 ID 或名稱）")

    df = pd.DataFrame(same_company_users)
    df = df.rename(columns={
        "id": "ID",
        "username": "使用者名稱",
        "is_admin": "是否為管理員",
        "company_name": "公司名稱",
        "note": "備註",
        "is_active": "啟用狀態"
    })
    df["是否為管理員"] = df["是否為管理員"].apply(lambda x: "✅" if x else "❌")
    df["啟用狀態"] = df["啟用狀態"].apply(lambda x: "🟢 啟用" if x else "⛔️ 已註銷")

    if search:
        df = df[
            df["使用者名稱"].str.contains(search, case=False) |
            df["ID"].astype(str).str.contains(search)
        ]

    items_per_page = 5
    total_pages = (len(df) - 1) // items_per_page + 1
    if "user_table_page" not in st.session_state:
        st.session_state["user_table_page"] = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ 上一頁") and st.session_state["user_table_page"] > 0:
            st.session_state["user_table_page"] -= 1
    with col2:
        st.markdown(f"**第 {st.session_state['user_table_page'] + 1} 頁 / 共 {total_pages} 頁**")
    with col3:
        if st.button("➡️ 下一頁") and st.session_state["user_table_page"] < total_pages - 1:
            st.session_state["user_table_page"] += 1

    start = st.session_state["user_table_page"] * items_per_page
    end = start + items_per_page
    paged_df = df.iloc[start:end]

    st.markdown("""
        <style>
        .styled-table {
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 16px;
            width: 100%;
            border: 1px solid #ddd;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .styled-table th, .styled-table td {
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: center;
        }
        .styled-table thead {
            background-color: #009879;
            color: #ffffff;
        }
        .styled-table tbody tr:hover {
            background-color: #f3f3f3;
        }
        </style>
    """, unsafe_allow_html=True)

    def df_to_html(df):
        html = '<table class="styled-table">'
        html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'
        html += '<tbody>'
        for _, row in df.iterrows():
            html += '<tr>' + ''.join(f'<td>{row[col]}</td>' for col in df.columns) + '</tr>'
        html += '</tbody></table>'
        return html

    if paged_df.empty:
        st.info("查無符合條件的使用者")
    else:
        st.markdown(df_to_html(paged_df), unsafe_allow_html=True)

        usernames_on_page = paged_df["使用者名稱"].tolist()
        selected_user = st.selectbox("✏️ 選擇使用者進行備註或註銷", usernames_on_page)

        selected_row = df[df["使用者名稱"] == selected_user]
        note_value = selected_row["備註"].values[0] if not selected_row.empty else ""
        note_input = st.text_input("📝 修改備註", value=note_value)

        col4, col5 = st.columns(2)
        with col4:
            if st.button("📀 儲存備註"):
                try:
                    res = requests.post(f"{API_BASE}/update_note", json={"username": selected_user, "note": note_input})
                    if res.status_code == 200:
                        st.success("✅ 備註已更新")
                        st.rerun()
                    else:
                        st.error("❌ 無法更新備註")
                except Exception as e:
                    st.error(f"❌ 系統錯誤：{str(e)}")

        with col5:
            user_active_status = selected_row["啟用狀態"].values[0] if not selected_row.empty else ""
            if user_active_status == "⛔️ 已註銷":
                st.warning("⚠️ 此帳號已註銷，無法重複操作")
            else:
                if st.button("⛔️ 註銷帳號"):
                    try:
                        res = requests.post(f"{API_BASE}/deactivate_user", json={"username": selected_user})
                        if res.status_code == 200:
                            st.success("⛔️ 已註銷帳號")
                            st.rerun()
                        else:
                            st.error("❌ 無法註銷帳號")
                    except Exception as e:
                        st.error(f"❌ 系統錯誤：{str(e)}")

    st.markdown("---")
    if st.button("⬅️ 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
