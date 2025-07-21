import streamlit as st
import requests
import zipfile
import tempfile
import os

API_BASE = "https://ocr-whisper-production-2.up.railway.app"

def get_current_user():
    return st.session_state.get("user")

def run():
    st.set_page_config(page_title="新增名片", page_icon="📇", layout="wide")
    st.title("📇 新增名片")

    user = get_current_user()
    if not user:
        st.warning("請先登入")
        return

    uploaded_files = st.file_uploader(
        "📤 上傳名片圖片（可多選 JPG/PNG 或 ZIP 壓縮檔）",
        type=["jpg", "jpeg", "png", "zip"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("請選擇圖片或壓縮檔上傳。")
        return

    preview_data = []

    def recognize_image(file_bytes, filename):
        files = {"file": (filename, file_bytes, "multipart/form-data")}
        try:
            res = requests.post(f"{API_BASE}/ocr", files=files)
            if res.ok:
                return res.json()
            else:
                st.warning(f"❌ {filename} 辨識失敗：{res.text}")
        except Exception as e:
            st.error(f"⚠️ 錯誤（{filename}）：{e}")
        return None

    for file in uploaded_files:
        if file.type == "application/zip":
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = os.path.join(tmp_dir, file.name)
                with open(zip_path, "wb") as f:
                    f.write(file.read())
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmp_dir)

                for fname in os.listdir(tmp_dir):
                    if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                        full_path = os.path.join(tmp_dir, fname)
                        with open(full_path, "rb") as img_f:
                            data = recognize_image(img_f, fname)
                            if data:
                                preview_data.append(data)
        else:
            data = recognize_image(file, file.name)
            if data:
                preview_data.append(data)

    if preview_data:
        st.subheader("🔍 預覽與送出")
        for i, card in enumerate(preview_data):
            with st.expander(f"名片 {i+1} 預覽"):
                name = st.text_input("姓名", value=card.get("name", ""), key=f"name_{i}")
                phone = st.text_input("電話", value=card.get("phone", ""), key=f"phone_{i}")
                email = st.text_input("Email", value=card.get("email", ""), key=f"email_{i}")
                title = st.text_input("職稱", value=card.get("title", ""), key=f"title_{i}")
                company_name = st.text_input("公司", value=card.get("company_name", ""), key=f"company_{i}")
                preview_data[i] = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "title": title,
                    "company_name": company_name
                }

        if st.button("✅ 一鍵送出全部資料", key="submit_button"):
            success_count = 0
            fail_count = 0
            for card in preview_data:
                card["user_id"] = user["id"]  # ✅ 傳入使用者 ID
                try:
                    res = requests.post(f"{API_BASE}/cards", json=card)
                    if res.ok:
                        success_count += 1
                    else:
                        st.error(f"❌ 儲存失敗：{res.text}")
                        fail_count += 1
                except Exception as e:
                    st.error(f"⚠️ 發生錯誤：{e}")
                    fail_count += 1
            st.success(f"✅ 成功儲存 {success_count} 筆，失敗 {fail_count} 筆")

    if st.button("🔙 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()
