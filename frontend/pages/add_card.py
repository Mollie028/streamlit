# frontend/pages/add_card.py

import streamlit as st
import requests
from PIL import Image
import io
import zipfile
import base64
from core.config import API_BASE


def add_card_page():
    st.markdown("## 📤 新增名片")
    st.caption("支援上傳 JPG / PNG 圖片或 ZIP 壓縮檔")

    uploaded_files = st.file_uploader(
        "拖曳檔案至此，或點選選取檔案",
        type=["jpg", "jpeg", "png", "zip"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if "extracted_results" not in st.session_state:
        st.session_state["extracted_results"] = []

    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(file.read()), "r") as zip_ref:
                    for name in zip_ref.namelist():
                        if name.lower().endswith((".jpg", ".jpeg", ".png")):
                            img_bytes = zip_ref.read(name)
                            process_and_store(name, img_bytes)
            else:
                img_bytes = file.read()
                process_and_store(file.name, img_bytes)

    # 顯示萃取結果（已美化）
    if st.session_state["extracted_results"]:
        st.markdown("### 🔍 預覽辨識結果")
        for i, r in enumerate(st.session_state["extracted_results"]):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(f"**📝 {r['filename']}**")
                st.markdown(format_fields(r["fields"]), unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state["extracted_results"].pop(i)
                    st.experimental_rerun()

    # 語音備註（選填）
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
            st.error("❌ 語音辨識失敗")

    # 一鍵送出
    if st.session_state["extracted_results"] and st.button("✅ 一鍵送出到資料庫"):
        uid = st.session_state["user"].get("id")
        token = st.session_state.get("access_token", "")
        headers = {"Authorization": f"Bearer {token}"}
        success = 0

        for r in st.session_state["extracted_results"]:
            payload = {
                "user_id": uid,
                "raw_text": r["raw_text"],
                "filename": r["filename"],
                "fields": r["fields"]
            }
            if note_text:
                payload["note"] = note_text

            res = requests.post(f"{API_BASE}/ocr", json=payload, headers=headers)
            if res.status_code == 200:
                success += 1

        st.success(f"✅ 成功送出 {success} 筆資料！")
        st.session_state["extracted_results"] = []


def process_and_store(filename, image_bytes):
    try:
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        files = {"file": (filename, image_bytes)}
        res = requests.post(f"{API_BASE}/ocr/", files=files, headers=headers)

        if res.status_code == 200:
            data = res.json()
            st.session_state["extracted_results"].append({
                "filename": filename,
                "raw_text": data.get("text", ""),
                "fields": data.get("fields", {})
            })
        else:
            st.error(f"❌ API 回傳失敗：{filename}，狀態碼 {res.status_code}")
    except Exception as e:
        st.error(f"❌ 辨識失敗：{filename}，錯誤訊息：{str(e)}")


def format_fields(fields: dict) -> str:
    if not fields:
        return "_無萃取欄位_"

    html = "<div style='line-height:1.8; font-size: 16px;'>"
    icon_map = {
        "name": "👤",
        "title": "🏷️",
        "phone": "📞",
        "email": "✉️",
        "company_name": "🏢"
    }

    for key, value in fields.items():
        icon = icon_map.get(key, "🔹")
        html += f"<b>{icon} {key}</b>：{value}<br>"

    html += "</div>"
    return html


def run():
    st.title("新增名片")
    try:
        add_card_page()
    except Exception as e:
        st.error("❌ 名片新增頁面載入失敗")
        st.code(str(e))

    # 👉 底部功能列：返回首頁 + 登出
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 返回首頁"):
            st.session_state["current_page"] = "home"
            st.rerun()
    with col2:
        if st.button("🚪 登出"):
            st.session_state.clear()
            st.session_state["current_page"] = "login"
            st.rerun()

