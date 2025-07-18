import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import requests
from core.config import API_BASE
from frontend.services.auth_service import is_logged_in, logout_button


def run():
    # ===================== ☁️ 登入狀態區塊 =====================
    if not is_logged_in():
        st.error("請先登入")
        st.stop()

    # ===================== 🔘 標題與登出 =====================
    st.set_page_config(page_title="新增名片")
    st.title("🆕 新增名片")
    logout_button()

    # ===================== 📤 上傳名片圖片 =====================
    st.subheader("📸 上傳名片圖片")
    image_file = st.file_uploader("請上傳名片圖片", type=["png", "jpg", "jpeg"])

    # ===================== 🎤 上傳語音備註 =====================
    st.subheader("🎙 上傳語音備註（選填）")
    audio_file = st.file_uploader("請上傳語音檔（.mp3 / .wav）", type=["mp3", "wav"])

    # ===================== 🚀 送出辨識請求 =====================
    if st.button("🚀 開始辨識"):

        if not image_file:
            st.warning("請上傳名片圖片")
        else:
            with st.spinner("辨識中，請稍候..."):

                # 傳送圖片與語音到後端
                files = {
                    "image": image_file,
                }
                if audio_file:
                    files["audio"] = audio_file

                try:
                    res = requests.post(
                        f"{API_BASE}/ocr_whisper",
                        files=files,
                        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                    )
                    result = res.json()

                    if res.status_code == 200:
                        st.success("辨識成功！")
                        st.subheader("📄 名片辨識結果：")
                        st.json(result.get("ocr_text", {}))

                        st.subheader("📝 語音備註轉文字：")
                        st.write(result.get("voice_text", "（無語音）"))

                        # 顯示送出按鈕
                        if st.button("✅ 確認送出"):
                            st.success("資料已送出（此功能可再串接資料庫）")

                    else:
                        st.error("辨識失敗，請確認圖片與語音格式")
                        st.code(result)

                except Exception as e:
                    st.error("系統錯誤")
                    st.code(str(e))

    # ===================== 🔙 返回按鈕 =====================
    st.markdown("---")
    if st.button("🔙 返回主選單"):
        role = st.session_state.get("role", "")
        if role == "admin":
            st.session_state["current_page"] = "account"
        else:
            st.session_state["current_page"] = "change_password"
        st.rerun()
