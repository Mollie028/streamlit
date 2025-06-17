import streamlit as st
import requests
def run():
    st.header("🎤 語音備註錄音")
    st.info("建議語音 3 秒以上")
    API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

    if "recorded" not in st.session_state:
        st.session_state.recorded = False
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "auto_sent" not in st.session_state:
        st.session_state.auto_sent = False

    if not st.session_state.recorded:
        audio = audio_recorder()
        if audio:
            audio_len = len(audio)
            if audio_len < 2000:
                st.error("⛔ 錄音檔為空，請確認麥克風已啟用。")
                st.stop()
            elif audio_len < 8000:
                st.warning("⚠️ 錄音時間太短（<3 秒），請再錄久一點。")
                st.stop()
            elif audio_len > 2_000_000:
                st.warning("⚠️ 錄音時間太長（>30 秒），請控制在 10～30 秒內。")
                st.stop()
            else:
                st.session_state.audio_data = audio
                st.session_state.recorded = True
                st.success("✅ 錄音完成，正在自動送出辨識...")
    else:
        st.audio(st.session_state.audio_data, format="audio/wav")
        if not st.session_state.auto_sent:
            with st.spinner("🧠 Whisper 語音辨識中..."):
                try:
                    files = {"file": ("audio.wav", st.session_state.audio_data, "audio/wav")}
                    res = requests.post(f"{API_BASE}/whisper", files=files)
                    res.raise_for_status()
                    st.session_state.transcript = res.json().get("text", "")
                    st.session_state.auto_sent = True
                    st.success("✅ Whisper 辨識完成！")
                except Exception as e:
                    st.error(f"❌ Whisper 發生錯誤：{e}")
                    st.stop()

        if st.session_state.transcript:
            st.text_area("📝 語音辨識結果", value=st.session_state.transcript, height=150)

        if st.button("🔁 重新錄音"):
            st.session_state.recorded = False
            st.session_state.auto_sent = False
            st.session_state.audio_data = None
            st.session_state.transcript = ""

    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))
