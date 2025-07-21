# frontend/pages/add_card.py

import streamlit as st
import requests
from PIL import Image
import io
import zipfile
import base64
from core.config import API_BASE


def add_card_page():
    st.markdown("## 新增名片")
    st.caption("📤 上傳名片圖片（可多選 JPG/PNG 或 ZIP 壓縮檔）")

    uploaded_files = st.file_uploader(
        "拖曳圖片或壓縮檔到這裡",
        type=["jpg", "jpeg", "png", "zip"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    results = []
    error_files = []

    if uploaded_files:
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

    # 顯示 OCR 預覽結果（無下拉，直接顯示）
    if results:
        st.markdown("---")
        st.markdown("### 🔍 預覽辨識結果")
        for r in results:
            st.image(r["image"], caption=r["filename"], use_column_width=True)
            st.markdown("#### 🧾 萃取欄位")
            st.json(r["fields"])  # 結構化欄位
            st.markdown("##### 🔤 原始文字")
            st.code(r["text"])

    # 語音備註（可選填）
    st.markdown("---")
    st.markdown("🎤 語音備註（可選填）")
    audio_file = st.file_uploader("上傳語音檔（mp3 / wav / m4a）", type=["mp3", "wav", "m4a"])
    note_text = ""

    if audio_file:
        st.audio(audio_file)
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        files = {"file": (audio_file.name, audio_file.read())}
        res = requests.post(f"{API_BASE}/whisper", files=files, headers=headers)
        if res.status_code == 200:
            note_text = res.json().get("text", "")
            st.success("✅ 語音辨識成功！")
            st.text_area("📝 語音內容", value=note_text, height=100)
        else:
            st.error("❌ 語音辨識失敗，請稍後再試")

    # 送出所有資料
    if results and st.button("✅ 一鍵送出到資料庫"):
        user = st.session_state.get("user", {})
        uid = user.get("id")
        token = st.session_state.get("access_token", "")
        headers = {"Authorization": f"Bearer {token}"}
        success = 0

        for r in results:
            payload = {
                "user_id": uid,
                "raw_text": r["text"],
                "filename": r["filename"],
                "fields": r["fields"]
            }
            if note_text:
                payload["note"] = note_text

            res = requests.post(f"{API_BASE}/cards", json=payload, headers=headers)
            if res.status_code == 200:
                success += 1
            else:
                st.error(f"❌ 上傳失敗：{r['filename']}，{res.text}")

        st.success(f"✅ 成功送出 {success} 筆資料！")

    if st.button("🔙 返回首頁"):
        st.session_state["current_page"] = "home"
        st.rerun()


def process_image(filename, image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_img = base64.b64encode(buffered.getvalue()).decode()

        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        files = {"file": (filename, image_bytes)}
        res = requests.post(f"{API_BASE}/ocr/", files=files, headers=headers)

        if res.status_code == 200:
            result = res.json()
            return {
                "filename": filename,
                "image": image,
                "text": result.get("raw_text", ""),
                "fields": result.get("fields", {})
            }
        else:
            st.error(f"❌ API 回傳失敗：{filename}，狀態碼 {res.status_code}，內容：{res.text}")
            return None
    except Exception as e:
        st.error(f"❌ 辨識過程錯誤：{filename}，錯誤訊息：{str(e)}")
        return None


# 給 app.py 呼叫的主入口
def run():
    st.title("新增名片")
    try:
        add_card_page()
    except Exception as e:
        st.error("❌ 名片新增頁面載入失敗，請稍後再試")
        st.code(str(e))
