import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

# ------------------------
# 設定與假資料
# ------------------------
st.set_page_config(page_title="名片辨識系統", layout="centered")
API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"
DUMMY_USERNAME = "testuser"
DUMMY_PASSWORD = "123456"
DUMMY_ROLE = "admin"
DUMMY_TOKEN = "fake-token"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

# ------------------------
# 登出按鈕（非登入頁才顯示）
# ------------------------
if st.session_state.get("access_token") and st.session_state["current_page"] != "login":
    if st.button("🔓 登出"):
        st.session_state.clear()
        st.session_state["current_page"] = "login"
        st.rerun()

# ------------------------
# 登入頁面
# ------------------------
if st.session_state["current_page"] == "login":
    st.title("🔐 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
            st.session_state["access_token"] = DUMMY_TOKEN
            st.session_state["username"] = DUMMY_USERNAME
            st.session_state["role"] = DUMMY_ROLE
            st.session_state["current_page"] = "home"
            st.rerun()
        else:
            st.error("❌ 帳號或密碼錯誤")

# ------------------------
# 首頁：依角色顯示功能
# ------------------------
elif st.session_state["current_page"] == "home":
    st.success(f"🎉 歡迎 {st.session_state['username']}（{st.session_state['role']}）")

    st.info("🛠️ 功能選單")
    if st.button("📷 拍照上傳名片"):
        st.session_state["current_page"] = "ocr"
        st.rerun()
    if st.button("🎤 錄音語音備註"):
        st.session_state["current_page"] = "voice"
        st.rerun()


# ------------------------
# 語音備註頁面
# ------------------------
elif st.session_state["current_page"] == "voice":
    st.header("🎤 語音備註錄音")
    st.info("建議語音 3 秒以上")

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
