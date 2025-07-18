import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import requests
from core.config import API_BASE
from services.auth_service import is_logged_in, logout_button


def run():
    # ☁️ 登入檢查
    if not is_logged_in():
        st.error("請先登入")
        st.stop()

    # ✅ 頁面設定
    st.set_page_config(page_title="新增名片")
    st.title("🆕 新增名片")
    logout_button()

    # 📸 上傳名片圖片
    st.subheader("📸 上傳名片圖片")
    image_file = st.file_uploader("請上傳名片圖片", type=["png", "jpg", "jpeg"])

    # 🎙️ 上傳語音備註（選填）
    st.subheader("🎤 上傳語音備註（選填）")
    audio_file = st.file_uploader("請上傳語音音檔（.mp3 / .wav）", type=["mp3", "wav"])

    ocr_result = None
    whisper_result = None

    # 🚀 開始辨識按鈕
    if st.button("🚀 開始辨識"):
        if not image_file:
            st.warning("請先上傳名片圖片")
            return

        with st.spinner("辨識中，請稍候..."):
            # ✅ 傳送圖片到後端 /ocr/
            try:
                ocr_response = requests.post(
                    f"{API_BASE}/ocr/",
                    files={"file": (image_file.name, image_file, image_file.type)},
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )
                if ocr_response.status_code == 200:
                    ocr_result = ocr_response.json()
                    st.success("✅ 名片圖片辨識成功")
                    st.subheader("📄 名片欄位內容：")
                    st.json(ocr_result.get("fields", {}))
                else:
                    st.error("❌ 圖片辨識失敗")
                    st.code(ocr_response.text)
            except Exception as e:
                st.error("❌ 傳送圖片錯誤")
                st.code(str(e))

            # ✅ 傳送語音檔（可選）
            if audio_file:
                try:
                    whisper_response = requests.post(
                        f"{API_BASE}/whisper/",
                        files={"audio": (audio_file.name, audio_file, audio_file.type)},
                        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                    )
                    if whisper_response.status_code == 200:
                        whisper_result = whisper_response.json()
                        st.success("✅ 語音轉文字成功")
                        st.subheader("📝 備註內容：")
                        st.write(whisper_result.get("text", ""))
                    else:
                        st.error("❌ 語音辨識失敗")
                        st.code(whisper_response.text)
                except Exception as e:
                    st.error("❌ 傳送語音錯誤")
                    st.code(str(e))
            else:
                st.info("ℹ️ 未上傳語音，略過語音辨識")

        # ✅ 確認送出按鈕（目前僅顯示訊息）
        if ocr_result:
            if st.button("✅ 確認送出"):
                st.success("資料已送出（你可以在此串接資料庫或 API）")

    # 🔙 返回主選單
    st.markdown("---")
    if st.button("🔙 返回主選單"):
        role = st.session_state.get("role", "")
        if role == "admin":
            st.session_state["current_page"] = "account"
        else:
            st.session_state["current_page"] = "change_password"
        st.rerun()
