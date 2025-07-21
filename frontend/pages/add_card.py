import streamlit as st
import requests
import zipfile
import tempfile
import os
from utils.session import get_current_user
from utils.api_base import API_BASE
from opencc import OpenCC

# --- 轉繁體工具 ---
cc = OpenCC('s2t')
def convert_to_traditional(text: str) -> str:
    return cc.convert(text)

st.set_page_config(page_title="新增名片", page_icon="📇", layout="wide")
st.title("📇 新增名片")

# --- 驗證登入狀態 ---
user = get_current_user()
if not user:
    st.warning("請先登入")
    st.stop()

# --- 上傳區 ---
uploaded_files = st.file_uploader(
    "請上傳名片圖片（可直接拍照、多選圖片或 ZIP 壓縮檔）",
    type=["jpg", "jpeg", "png", "zip"],
    accept_multiple_files=True,
    label_visibility="visible"
)

if not uploaded_files:
    st.info("請上傳至少一張名片圖片或壓縮檔。")
    st.stop()

preview_data = []

# --- 處理所有上傳檔案 ---
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
                            st.error(f"⚠️ 錯誤（{fname}）：{e}")
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
            st.error(f"⚠️ 錯誤（{file.name}）：{e}")

# --- 預覽區與送出按鈕 ---
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
                st.error(f"⚠️ 儲存錯誤：{e}")
                fail_count += 1
        st.success(f"✅ 成功儲存 {success_count} 筆，失敗 {fail_count} 筆")

# --- 返回主頁 ---
if st.button("🔙 返回主頁"):
    st.switch_page("app.py")
