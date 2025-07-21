import streamlit as st
import requests
import zipfile
import tempfile
import os
from opencc import OpenCC

# ✅ 模擬 utils.session.get_current_user
def get_current_user():
    return st.session_state.get("user")

# ✅ 模擬 utils.api_base.API_BASE
API_BASE = "https://ocr-whisper-production-2.up.railway.app"

# ✅ 轉換簡體為繁體
cc = OpenCC("s2t")
def convert_to_traditional(text: str) -> str:
    return cc.convert(text)

st.set_page_config(page_title="新增名片", page_icon="📇", layout="wide")
st.title("📇 新增名片")

user = get_current_user()
if not user:
    st.warning("請先登入")
    st.stop()

uploaded_files = st.file_uploader(
    "📷 請上傳名片圖片（支援手機拍照、多選、ZIP 壓縮）",
    type=["jpg", "jpeg", "png", "zip"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("請選擇圖片或壓縮檔上傳。")
    st.stop()

preview_data = []

# 🔄 處理所有上傳的圖片或壓縮檔
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
                    with open(os.path.join(tmp_dir, fname), "rb") as img_f:
                        files = {"file": (fname, img_f, "multipart/form-data")}
                        try:
                            res = requests.post(f"{API_BASE}/ocr", files=files)
                            if res.ok:
                                data = res.json()
                                for k in data:
                                    if isinstance(data[k], str):
                                        data[k] = convert_to_traditional(data[k])
                                preview_data.append(data)
                            else:
                                st.warning(f"❌ {fname} 辨識失敗：{res.text}")
                        except Exception as e:
                            st.error(f"⚠️ {fname} 發生錯誤：{e}")
    else:
        files = {"file": (file.name, file, "multipart/form-data")}
        try:
            res = requests.post(f"{API_BASE}/ocr", files=files)
            if res.ok:
                data = res.json()
                for k in data:
                    if isinstance(data[k], str):
                        data[k] = convert_to_traditional(data[k])
                preview_data.append(data)
            else:
                st.warning(f"❌ {file.name} 辨識失敗：{res.text}")
        except Exception as e:
            st.error(f"⚠️ {file.name} 發生錯誤：{e}")

# ✅ 顯示預覽並送出
if preview_data:
    st.subheader("🔍 預覽名片資料與送出")
    for i, card in enumerate(preview_data):
        with st.expander(f"名片 {i+1}"):
            name = st.text_input("姓名", value=card.get("name", ""), key=f"name_{i}")
            phone = st.text_input("電話", value=card.get("phone", ""), key=f"phone_{i}")
            email = st.text_input("Email", value=card.get("email", ""), key=f"email_{i}")
            title = st.text_input("職稱", value=card.get("title", ""), key=f"title_{i}")
            company = st.text_input("公司", value=card.get("company_name", ""), key=f"company_{i}")
            preview_data[i] = {
                "name": name,
                "phone": phone,
                "email": email,
                "title": title,
                "company_name": company
            }

    if st.button("✅ 一鍵送出全部資料"):
        success_count = 0
        fail_count = 0
        for card in preview_data:
            try:
                res = requests.post(f"{API_BASE}/cards", json=card)
                if res.ok:
                    success_count += 1
                else:
                    st.error(f"❌ 儲存失敗：{res.text}")
                    fail_count += 1
            except Exception as e:
                st.error(f"⚠️ 錯誤：{e}")
                fail_count += 1
        st.success(f"✅ 成功儲存 {success_count} 筆，失敗 {fail_count} 筆")

# 🔙 返回主頁按鈕
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")
