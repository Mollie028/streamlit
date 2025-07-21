import streamlit as st
import requests
from PIL import Image
import io

API_BASE = "https://ocr-whisper-production-2.up.railway.app"  # 依你的實際後端 API URL 調整

def run():
    st.title("➕ 新增名片")

    # 回主選單
    if st.button("🔙 返回主選單"):
        st.session_state["current_page"] = "home"
        st.rerun()

    # 使用者資訊
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    uploaded_files = st.file_uploader("📤 上傳名片圖片（支援多張）", type=["jpg", "png", "jpeg", "webp"], accept_multiple_files=True)

    audio_bytes = st.file_uploader("🎤 上傳語音備註（選填，支援 mp3/wav）", type=["mp3", "wav", "m4a"])

    if uploaded_files:
        st.markdown("### 🖼️ 預覽上傳圖片與辨識結果")
        results = []

        for file in uploaded_files:
            image = Image.open(file)
            st.image(image, caption=file.name, use_column_width=True)

            with st.spinner("辨識中..."):
                files = {"file": (file.name, file, file.type)}
                try:
                    res = requests.post(f"{API_BASE}/ocr", files=files)
                    if res.status_code == 200:
                        data = res.json()
                        st.success("✅ 名片文字辨識成功")
                        st.code(data["text"])
                        results.append(data)
                    else:
                        st.error(f"❌ 辨識失敗：{res.status_code}")
                        st.code(res.text)
                except Exception as e:
                    st.error("❌ 連線失敗")
                    st.code(str(e))

        if audio_bytes:
            st.markdown("---")
            st.markdown("### 🎧 語音備註辨識結果")
            try:
                files = {"file": ("note.wav", audio_bytes, "audio/wav")}
                res = requests.post(f"{API_BASE}/whisper", files=files)
                if res.status_code == 200:
                    whisper_result = res.json()
                    st.success("✅ 語音辨識成功")
                    st.code(whisper_result["text"])
                else:
                    st.error("❌ 語音辨識失敗")
                    st.code(res.text)
            except Exception as e:
                st.error("❌ 語音辨識錯誤")
                st.code(str(e))
        else:
            whisper_result = None

        # 一鍵送出
        if st.button("✅ 一鍵送出到資料庫"):
            for data in results:
                payload = {
                    "user_id": user_id,
                    "raw_text": data["text"],
                    "fields": data.get("fields", {}),
                }
                try:
                    res = requests.post(f"{API_BASE}/extract", json=payload)
                    if res.status_code == 200:
                        st.success("📥 成功寫入資料庫！")
                    else:
                        st.error("❌ 寫入失敗")
                        st.code(res.text)
                except Exception as e:
                    st.error("❌ 送出錯誤")
                    st.code(str(e))

            # 如果語音備註有辨識，也一併送出
            if whisper_result:
                try:
                    payload = {
                        "user_id": user_id,
                        "raw_text": whisper_result["text"],
                    }
                    res = requests.post(f"{API_BASE}/save_voice_note", json=payload)
                    if res.status_code == 200:
                        st.success("📝 語音備註已儲存")
                    else:
                        st.warning("❗ 無法儲存語音備註")
                except Exception as e:
                    st.error("❌ 備註送出錯誤")
                    st.code(str(e))
