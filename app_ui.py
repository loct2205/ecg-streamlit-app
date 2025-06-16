# app_ui.py

import streamlit as st
import requests
from PIL import Image
import io
import base64

st.set_page_config(page_title="Hỗ Trợ Chẩn Đoán ECG", layout="wide")

# Giao diện chính
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Hỗ Trợ Chẩn Đoán Tín Hiệu Điện Tim (ECG)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Tải lên tệp ECG (.mat) để hệ thống dự đoán và hiển thị biểu đồ</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Chọn tệp .mat", type=["mat"])

if uploaded_file is not None:
    with st.spinner("⏳ Đang xử lý tín hiệu ECG..."):
        # Upload file to FastAPI server
        files = {'file': uploaded_file}
        try:
            API_URL = "https://heartpredict.duckdns.org/predict/"
            response = requests.post(API_URL, files=files)

            if response.status_code == 200:
                result = response.json()
                prediction = result.get("prediction", {})
                image_base64 = result.get("ecg_plot_base64", "")

                st.success("✅ Hoàn tất phân tích tín hiệu!")

                # Show ECG image
                st.markdown("### 📈 Sơ đồ điện tim")
                if image_base64:
                    image_bytes = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, use_column_width='always', caption="Sơ đồ điện tim")

                # Show predicted result
                st.markdown("### 🔍 Kết quả dự đoán")
                if isinstance(prediction, dict):
                    for label, value in prediction.items():
                        st.markdown(f"<div style='font-size:18px'><b>{label}</b>: {round(value, 3)}</div>", unsafe_allow_html=True)
                elif isinstance(prediction, list):
                    st.write(prediction)
                else:
                    st.write(str(prediction))
            else:
                st.error(f"❌ Lỗi từ API: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("🚫 Không thể kết nối tới API. Hãy kiểm tra xem FastAPI đã được khởi động chưa.")
