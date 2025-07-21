import streamlit as st
import requests
import zipfile
import tempfile
import os
from utils.session import get_current_user
from utils.api_base import API_BASE

st.set_page_config(page_title="新增名片", page_icon="📇", layout="wide")
st.title("📇 新增名片")

# 檢查登入
user = get_current_user()
if not user:
    st.warning("請先登入")
    st.stop()

# 上傳圖片或 zip
uploaded_files = st.file_uploader(
    "請上傳名片圖片（可多選 JPG/PNG 或 ZIP 壓縮檔）",
    type=["jpg", "jpeg", "png", "zip"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("請選擇圖片或壓縮檔上傳。")
    st.stop()

preview_data = []

# 將圖片送 API 做 OCR
def process_image_file(file_obj, fname):
    files = {"file": (fname, file_obj, "multipart/form-data")}
    try:
        res = requests.post(f"{API_BASE}/ocr", files=files)
        if res.ok:
            data = res.json()
            preview_data.append(data)
        else:
            st.warning(f"❌ {fname} 辨識失敗：{res.text}")
    except Exception as e:
        st.error(f"⚠️ 錯誤（{fname}）：{e}")

# 處理每個上傳的檔案
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
                        process_image_file(img_f, fname)
    else:
        process_image_file(file, file.name)

# 顯示辨識結果與送出
if preview_data:
    st.subheader("🔍 預覽與送出")
    for i, card in enumerate(preview_data):
        with st.expander(f"名片 {i+1}"):
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
        st.success(f"✅ 已成功儲存 {success_count} 筆，失敗 {fail_count} 筆")

# 返回主頁
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")
