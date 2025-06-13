import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

# ─── 後端 API 基礎網址 ───────────────────────────────
API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

# ─── 頁面設定 ───────────────────────────────────────
st.set_page_config(page_title="名片辨識系統", layout="centered")

# ─── 登入邏輯：未登入前只顯示登入畫面 ─────────────────
if "token" not in st.session_state:
    st.title("🔐 請先登入")
    user = st.text_input("帳號")
    pwd  = st.text_input("密碼", type="password")
    if st.button("登入"):
        res = requests.post(
            f"{API_BASE}/login",
            json={"username": user, "password": pwd}
        )
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.success("登入成功，重新整理中…")
            st.rerun()
        else:
            st.error("登入失敗，請再確認帳號密碼")
    st.stop()

# ─── 登出按鈕（選做）────────────────────────────────
if st.button("🔓 登出"):
    st.session_state.pop("token", None)
    st.rerun()

# ─── 主畫面標題 ───────────────────────────────────────
st.title("名片辨識 + 語音備註系統")

# ─── 統一帶入 Authorization header ───────────────────
headers = {"Authorization": f"Bearer {st.session_state.token}"}

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
                res = requests.post(
                    f"{API_BASE}/ocr",
                    files=files,
                    headers=headers
                )
                res.raise_for_status()

                ocr_response = res.json()
                text = ocr_response.get("text", "").strip()
                record_id = ocr_response.get("id")

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
                                payload = {"text": user_input, "id": record_id}
                                llama_res = requests.post(
                                    f"{API_BASE}/extract",
                                    json=payload,
                                    headers=headers
                                )
                                llama_res.raise_for_status()
                                st.success("✅ LLaMA 採集結果：")
                                st.json(llama_res.json())
                            except Exception as e:
                                st.error(f"❌ LLaMA 分析失敗：{e}")
            except Exception as e:
                st.error(f"❌ OCR 發生錯誤：{e}")

# ------------------------
# 🎤 語音備註錄音
# ------------------------
st.header("語音備註錄音")
st.info("建議語音 3 秒以上")

# 初始化 session_state
if "recorded" not in st.session_state:
    st.session_state.recorded = False
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "auto_sent" not in st.session_state:
    st.session_state.auto_sent = False

# 錄音階段
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
                files = {
                    "file": ("audio.wav", st.session_state.audio_data, "audio/wav")
                }
                res = requests.post(
                    f"{API_BASE}/whisper",
                    files=files,
                    headers=headers
                )
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

# 最後顯示一次辨識結果（如果有）
if st.session_state.transcript:
    st.text_area("📝 語音辨識結果", value=st.session_state.transcript, height=150)

st.write("App 啟動成功！")
