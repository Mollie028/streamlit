import streamlit as st
import requests

print("🧪 [pages/ocr.py] 模組已載入")

def run():

    st.header("📷 名片辨識（支援多張）")
    API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app"

    img_files = st.file_uploader("請上傳名片圖片（支援 jpg/png）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if img_files:
        for img_file in img_files:
            st.image(img_file, caption=f"預覽：{img_file.name}", width=300)
            with st.spinner(f"🔍 OCR 辨識中：{img_file.name}"):
                try:
                    files = {"file": (img_file.name, img_file.getvalue(), img_file.type)}
                    res = requests.post(f"{API_BASE}/ocr", files=files)
                    res.raise_for_status()
                    ocr_response = res.json()
                    text = ocr_response.get("text", "").strip()
                    record_id = ocr_response.get("id")
                    if not text:
                        st.warning(f"⚠️ {img_file.name} 沒有辨識出任何文字")
                    else:
                        user_input = st.text_area(f"📄 {img_file.name} OCR 辨識結果（可修改）", value=text, height=200)
                        if st.button(f"✅ 確認送出 LLaMA 分析：{img_file.name}", key=img_file.name):
                            with st.spinner("進行資料萃取..."):
                                try:
                                    payload = {"text": user_input, "id": record_id}
                                    llama_res = requests.post(f"{API_BASE}/extract", json=payload)
                                    llama_res.raise_for_status()
                                    st.success("✅ LLaMA 採集結果：")
                                    st.json(llama_res.json())
                                except Exception as e:
                                    st.error(f"❌ LLaMA 分析失敗：{e}")
                except Exception as e:
                    st.error(f"❌ OCR 發生錯誤：{e}")

    st.button("⬅️ 返回首頁", on_click=lambda: st.session_state.update(current_page="home"))
