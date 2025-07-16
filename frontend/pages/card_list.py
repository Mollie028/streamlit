import streamlit as st
import requests
from core.config import API_BASE

st.subheader("📇 名片清單")

# 根據身分決定是否顯示所有名片
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "")
headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

# 查詢名片
try:
    if role == "admin":
        res = requests.get(f"{API_BASE}/cards", headers=headers)
    else:
        res = requests.get(f"{API_BASE}/cards?username={username}", headers=headers)

    cards = res.json()
    if not cards:
        st.info("尚未有名片資料")
    else:
        for card in cards:
            with st.expander(f"📛 {card.get('name', '(無名)')} - {card.get('company_name', '(無公司)')}"):
                st.write(f"✉️ Email: {card.get('email')}")
                st.write(f"📞 Phone: {card.get('phone')}")
                st.write(f"🏷️ Title: {card.get('title')}")
                st.write(f"🏢 Company: {card.get('company_name')}")
                st.write(f"📝 Raw Text: {card.get('raw_text')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ 編輯 - {card['id']}", key=f"edit_{card['id']}"):
                        st.session_state["edit_card_id"] = card['id']
                        st.session_state["current_page"] = "ocr"  # 重新導向到編輯頁
                        st.rerun()
                with col2:
                    if st.button(f"🗑️ 刪除 - {card['id']}", key=f"delete_{card['id']}"):
                        confirm = st.radio(f"確定刪除 {card['name']} 的名片？", ("否", "是"), key=f"confirm_{card['id']}")
                        if confirm == "是":
                            del_res = requests.delete(f"{API_BASE}/cards/{card['id']}", headers=headers)
                            if del_res.status_code == 200:
                                st.success("✅ 已成功刪除名片")
                                st.rerun()
                            else:
                                st.error("❌ 名片刪除失敗")

except Exception as e:
    st.error("❌ 讀取名片清單失敗")
    st.code(str(e))

# 匯出功能（未來可擴充）
st.markdown("---")
st.download_button("📤 匯出所有名片資料（JSON）", data=str(cards), file_name="cards.json")
