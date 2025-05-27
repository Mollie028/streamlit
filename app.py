import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

st.set_page_config(page_title="名片辨識系統", layout="centered")
st.title("名片辨識 + 語音備註系統")

# ------------------------
# 📄 上傳多張名片圖片
# ------------------------
st.header("上傳名片圖片（支援多張）")
img_files = st.file_uploader(
    "請上傳名片圖片（支援 jpg/png）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if img_files:
    for img_file in img_files:
        st.image(img_file, caption=f"預覽：{img_file.name}", width=300)
        with st.spinner(f"🔍 OCR 辨識中：{img_file.name}"):
            try:
                files = {"file": (img_file.name, img_file.getvalue(), img_file.type)}
                res = requests.post(f"{API_BASE}/ocr", files=files)

                st.write("✅ API 回應碼：", res.status_code)
                st.write("✅ API 回應內容：", res.text)
                res.raise_for_status()

                ocr_response = res.json()
                text = ocr_response.get("text", "").strip()
                record_id = ocr_response.get("id")  # ✅ 抓出 OCR 回傳的 id

                if not text:
                    st.warning(f"⚠️ {img_file.name} 沒有辨識出任何文字")
                else:
                    user_input = st.text_area(
                        f"📄 {img_file.name} OCR 辨識結果（可修改）",
                        value=text,
                        height=200,
                    )
                    if st.button(f"✅ 確認送出 LLaMA 分析：{img_file.name}", key=img_file.name):
                        with st.spinner("進行資料萃取..."):
                            try:
                                payload = {
                                    "text": user_input,
                                    "id": record_id  # ✅ 加入 id
                                }
                                llama_res = requests.post(f"{API_BASE}/extract", json=payload)
                                llama_res.raise_for_status()
                                st.success("✅ LLaMA 採集結果：")
                                st.json(llama_res.json())
                            except Exception as e:
                                st.error(f"❌ LLaMA 分析失敗：{e}")
            except Exception as e:
                st.error(f"❌ OCR 發生錯誤：{e}")
# ------------------------
# 🎤 語音備註錄音（streamlit-audiorecorder）
# ------------------------
st.header("🎤 語音備註錄音")
st.info("🟢 點下錄音後請停一秒再開始講話，建議語音 3 秒以上。")

# 初始化 session_state 狀態
if "recorded" not in st.session_state:
    st.session_state.recorded = False
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

# 錄音階段
if not st.session_state.recorded:
    audio = audio_recorder()
    if audio:
        st.session_state.audio_data = audio
        st.session_state.recorded = True
        st.success("✅ 錄音完成！你可以播放或送出辨識。")
else:
    st.audio(st.session_state.audio_data, format="audio/wav")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔁 重新錄音"):
            st.session_state.recorded = False
            st.session_state.audio_data = None
            st.session_state.transcript = ""

    with col2:
        if st.button("✅ 傳送語音辨識"):
            with st.spinner("🧠 Whisper 語音辨識中..."):
                try:
                    files = {
                        "file": ("audio.wav", st.session_state.audio_data, "audio/wav")
                    }
                    res = requests.post(f"{API_BASE}/whisper", files=files)
                    res.raise_for_status()
                    st.session_state.transcript = res.json().get("text", "")
                    st.success("✅ Whisper 辨識成功！")
                except Exception as e:
                    st.error(f"❌ Whisper 發生錯誤：{e}")

if st.session_state.transcript:
    st.text_area("📝 語音辨識結果", value=st.session_state.transcript, height=150)
st.write("App 啟動成功！")
