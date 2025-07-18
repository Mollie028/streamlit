import sys
import os

# 加入 streamlit 根目錄到 Python 搜尋路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import requests
from core.config import API_BASE
from services.auth_service import is_logged_in, logout_button


def run():
    # ☁️ 登入狀態區塊
    if not is_logged_in():
        st.error("請先登入")
        st.stop()

    # 🔘 標題與登出
    st.set_page_config(page_title="新增名片")
    st.title("🆕 新增名片")
    logout_button()

    # 📤 上傳名片圖片
    st.subheader("📸 上傳名片圖片")
    image_file = st.file_uploader("請上傳名片圖片", type=["png", "jpg", "jpeg"])

    # 🎤 上傳語音備註
    st.subheader("🎙 上傳語音備註（選填）")
    audio_file = st.file_uploader("請上傳語音檔（.mp3 / .wav）", type=["mp3", "wav"])

    # 🚀 送出辨識請求
    if st.button("🚀 開始辨識"):
        if not image_file:
            st.warning("請上傳名片圖片")
            return

        with st.spinner("辨識中，請稍候..."):

            ocr_text = None
            voice_text = None

            # ✅ 傳送圖片到 /ocr
            try:
                ocr_res = requests.post(
                    f"{API_BASE}/ocr",
                    files={"image": (image_file.name, image_file, image_file.type)},
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )
                if ocr_res.status_code == 200:
                    ocr_text = ocr_res.json()
                else:
                    st.error("❌ 圖片辨識失敗")
                    st.code(ocr_res.text)
            except Exception as e:
                st.error("❌ 傳送圖片錯誤")
                st.code(str(e))

            # ✅ 傳送語音到 /whisper（如果有）
            if audio_file:
                try:
                    whisper_res = requests.post(
                        f"{API_BASE}/whisper",
                        files={"audio": (audio_file.name, audio_file, audio_file.type)},
                        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                    )
                    if whisper_res.status_code == 200:
                        voice_text = whisper_res.json()
                    else:
                        st.error("❌ 語音轉文字失敗")
                        st.code(whisper_res.text)
                except Exception as e:
                    st.error("❌ 傳送語音錯誤")
                    st.code(str(e))

            # ✅ 顯示結果
            if ocr_text:
                st.success("✅ 圖片辨識成功！")
                st.subheader("📄 名片辨識結果：")
                st.json(ocr_text)
            else:
                st.warning("⚠️ 名片辨識沒有成功結果")

            if voice_text:
                st.success("✅ 語音轉文字成功！")
                st.subheader("📝 語音備註：")
                st.write(voice_text)
            elif audio_file:
                st.warning("⚠️ 無語音辨識結果")

            # ✅ 顯示送出按鈕
            if ocr_text:
                if st.button("✅ 確認送出"):
                    st.success("資料已送出（此功能可再串接資料庫）")

    # 🔙 返回按鈕
    st.markdown("---")
    if st.button("🔙 返回主選單"):
        role = st.session_state.get("role", "")
        if role == "admin":
            st.session_state["current_page"] = "account"
        else:
            st.session_state["current_page"] = "change_password"
        st.rerun()
