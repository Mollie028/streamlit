# frontend/components/add_card.py
import streamlit as st
import requests
from PIL import Image
import io
import zipfile
import base64
from core.config import API_BASE

def add_card_page():
    st.markdown("### 🆕 新增名片")
    st.caption("📤 上傳名片圖片（可多選 JPG/PNG 或 ZIP 壓縮檔）")

    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        type=["jpg", "jpeg", "png", "zip"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if not uploaded_files:
        st.info("請選擇圖片或壓縮檔上傳。")
        return

    results = []
    error_files = []

    for file in uploaded_files:
        if file.name.endswith(".zip"):
            zip_bytes = io.BytesIO(file.read())
            with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
                for name in zip_ref.namelist():
                    if name.lower().endswith((".jpg", ".jpeg", ".png")):
                        img_bytes = zip_ref.read(name)
                        result = process_image(name, img_bytes)
                        if result:
                            results.append(result)
                        else:
                            error_files.append(name)
        else:
            img_bytes = file.read()
            result = process_image(file.name, img_bytes)
            if result:
                results.append(result)
            else:
                error_files.append(file.name)

    if error_files:
        st.warning("❌ 以下檔案辨識失敗：")
        st.write(", ".join(error_files))

    if results:
        st.markdown("---")
        st.markdown("### 🔍 預覽與確認")
        for r in results:
            with st.expander(f"📇 {r['filename']}"):
                st.image(r["image"], use_column_width=True)
                st.code(r["text"])

        if st.button("✅ 一鍵送出到資料庫"):
            user = st.session_state.get("user", {})
            uid = user.get("id")
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            success = 0
            for r in results:
                payload = {
                    "user_id": uid,
                    "raw_text": r["text"],
                    "filename": r["filename"]
                }
                res = requests.post(f"{API_BASE}/ocr", json=payload, headers=headers)
                if res.status_code == 200:
                    success += 1
            st.success(f"✅ 成功送出 {success} 筆資料！")

    if st.button("🔙 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()

# 處理單張圖片邏輯
def process_image(filename, image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        b64_img = base64.b64encode(buffered.getvalue()).decode()

        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        files = {"file": (filename, image_bytes)}
        res = requests.post(f"{API_BASE}/ocr_image", files=files, headers=headers)
        if res.status_code == 200:
            text = res.json().get("text", "")
            return {"filename": filename, "image": image, "text": text}
        return None
    except Exception as e:
        return None
