import streamlit as st
import requests
import zipfile
import tempfile
import os

def get_current_user():
    return st.session_state.get("user")

API_BASE = "https://ocr-whisper-production-2.up.railway.app"
st.set_page_config(page_title="新增名片", page_icon="📇", layout="wide")
st.title("📇 新增名片")

user = get_current_user()
if not user:
    st.warning("請先登入")
    st.stop()

# 初始化 Session State
if "preview_data" not in st.session_state:
    st.session_state["preview_data"] = []

# 上傳檔案
uploaded_files = st.file_uploader(
    "📤 上傳名片圖片（可多選 JPG/PNG 或 ZIP 壓縮檔）",
    type=["jpg", "jpeg", "png", "zip"],
    accept_multiple_files=True
)

def recognize_image(file_bytes, filename):
    files = {"file": (filename, file_bytes, "multipart/form-data")}
    try:
        res = requests.post(f"{API_BASE}/ocr", files=files)
        if res.ok:
            data = res.json()
            data["voice_note"] = ""
            return data
        else:
            st.warning(f"❌ {filename} 辨識失敗：{res.text}")
    except Exception as e:
        st.error(f"⚠️ 錯誤（{filename}）：{e}")
    return None

# 進行辨識
if uploaded_files:
    for file in uploaded_files:
        if file.type == "application/zip":
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = os.path.join(tmp_dir, file.name)
                with open(zip_path, "wb") as f:
                    f.write(file.read())
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmp_dir)

                for fname in os.listdir(tmp_dir):
                    if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                        full_path = os.path.join(tmp_dir, fname)
                        with open(full_path, "rb") as img_f:
                            result = recognize_image(img_f, fname)
                            if result:
                                st.session_state["preview_data"].append(result)
        else:
            result = recognize_image(file, file.name)
            if result:
                st.session_state["preview_data"].append(result)

# 顯示預覽區
preview_data = st.session_state["preview_data"]
if preview_data:
    st.subheader("🔍 預覽與語音備註")
    for i, card in enumerate(preview_data):
        with st.expander(f"名片 {i+1}"):
            name = st.text_input("姓名", value=card.get("name", ""), key=f"name_{i}")
            phone = st.text_input("電話", value=card.get("phone", ""), key=f"phone_{i}")
            email = st.text_input("Email", value=card.get("email", ""), key=f"email_{i}")
            title = st.text_input("職稱", value=card.get("title", ""), key=f"title_{i}")
            company = st.text_input("公司", value=card.get("company_name", ""), key=f"company_{i}")

            st.markdown("🎤 **語音備註**（可選）")
            voice_note = card.get("voice_note", "")
            if voice_note:
                st.success("✅ 語音備註轉換成功")
                st.write(voice_note)

            audio = st.file_uploader("上傳語音（mp3/wav/m4a）", type=["mp3", "wav", "m4a"], key=f"audio_{i}")
            if audio:
                files = {"file": (audio.name, audio, "multipart/form-data")}
                try:
                    res = requests.post(f"{API_BASE}/whisper", files=files)
                    if res.ok:
                        voice_note = res.json().get("text", "")
                        st.success("✅ 語音備註轉換成功")
                        st.write(voice_note)
                    else:
                        st.warning("❌ 語音辨識失敗")
                except Exception as e:
                    st.error(f"⚠️ 語音錯誤：{e}")

            preview_data[i] = {
                "name": name,
                "phone": phone,
                "email": email,
                "title": title,
                "company_name": company,
                "voice_note": voice_note
            }

    if st.button("✅ 一鍵送出全部資料"):
        success_count = 0
        for card in preview_data:
            try:
                res = requests.post(f"{API_BASE}/cards", json=card)
                if res.ok:
                    success_count += 1
                else:
                    st.error(f"❌ 儲存失敗：{res.text}")
            except Exception as e:
                st.error(f"⚠️ 儲存錯誤：{e}")
        st.success(f"✅ 成功儲存 {success_count} 筆資料")
        st.session_state["preview_data"] = []  # 清除預覽資料

    st.markdown("🔙 [返回主頁](./)")

elif not uploaded_files:
    st.info("請選擇圖片或壓縮檔上傳。")
