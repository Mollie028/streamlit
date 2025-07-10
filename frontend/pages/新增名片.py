import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from core.config import API_BASE

st.subheader("➕ 新增名片（含語音備註）")

# ----------- 上傳名片圖片辨識 -----------
st.markdown("### 📷 上傳名片圖片")
image_file = st.file_uploader("請選擇一張名片圖片", type=["jpg", "jpeg", "png"])

if image_file:
    if st.button("🔍 開始辨識"):
        with st.spinner("辨識中..."):
            try:
                files = {"image": image_file.getvalue()}
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                res = requests.post(f"{API_BASE}/ocr", files=files, headers=headers)
                if res.status_code == 200:
                    result = res.json()
                    st.success("✅ 名片已辨識")
                    st.json(result)
                else:
                    st.error("❌ 名片辨識失敗")
            except Exception as e:
                st.error("❌ 名片辨識發生錯誤")
                st.code(str(e))

# ----------- 錄音語音備註 -----------
st.markdown("### 🎤 錄製語音備註")
audio_bytes = audio_recorder(text="點擊開始 / 結束錄音", pause_threshold=3.0, sample_rate=16000)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    if st.button("🧠 傳送語音進行辨識"):
        with st.spinner("語音辨識中..."):
            try:
                files = {"audio": audio_bytes}
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                res = requests.post(f"{API_BASE}/whisper", files=files, headers=headers)
                if res.status_code == 200:
                    result = res.json()
                    st.success("✅ 語音辨識完成")
                    st.write(result["transcription"])
                else:
                    st.error("❌ 語音辨識失敗")
            except Exception as e:
                st.error("❌ 系統錯誤")
                st.code(str(e))
