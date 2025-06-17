# app_ui.py
import gc
import streamlit as st
import requests
from PIL import Image
import io
import base64

st.set_page_config(page_title="Hỗ Trợ Chẩn Đoán Tín Hiệu Điện Tim (ECG)", layout="wide")

label_map = {
    0: ("NORM", "Bình thường"),
    1: ("AF", "Rung tâm nhĩ"),
    2: ("I-AVB", "Block nhĩ thất độ I"),
    3: ("LBBB", "Block nhánh trái"),
    4: ("RBBB", "Block nhánh phải"),
    5: ("PAC", "Co tâm nhĩ sớm"),
    6: ("PVC", "Co tâm thất sớm"),
    7: ("STD", "Đoạn ST chênh xuống"),
    8: ("STE", "Đoạn ST tăng cao")
}

# UI
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Hỗ Trợ Chẩn Đoán Tín Hiệu Điện Tim (ECG)</h1>",
            unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size:18px;'>Tải lên tệp ECG (.mat) để hệ thống dự đoán và hiển thị biểu đồ</p>",
    unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Chọn tệp .mat", type=["mat"])

if uploaded_file is not None:
    with st.spinner("⏳ Đang dự đoán tín hiệu điện tim..."):
        # Upload file to FastAPI server
        files = {'file': uploaded_file}
        record_id = ""
        try:
            API_URL = "https://heartpredict.duckdns.org/predict/"
            response = requests.post(API_URL, files=files)

            if response.status_code == 200:
                result = response.json()
                prediction = result.get("prediction", {})
                record_id = result.get("record_id", "")
                #image_base64 = result.get("ecg_plot_base64", "")

                # Show predicted result
                st.markdown("### 🔍 Kết quả dự đoán")
                if isinstance(prediction, dict) and "mean_probs" in prediction:
                    probs = prediction["mean_probs"]
                    threshold = 0.3
                    for idx, prob in enumerate(probs):
                        if prob > threshold:
                            label, desc = label_map.get(idx, (f"Label {idx}", "Không rõ"))
                            st.markdown(
                                f"<div style='font-size:18px;'>🔹 <b>{label}</b> — {desc}: "
                                f"<span style='color:#FF5733'>{round((prob*100), 2)}&nbsp;%</span></div>",
                                unsafe_allow_html=True
                            )

            else:
                st.error(f"❌ Lỗi từ API: {response.status_code}")
                st.stop()
        except requests.exceptions.ConnectionError:
            st.error("🚫 Không thể kết nối tới API. Hãy kiểm tra xem FastAPI đã được khởi động chưa.")
            st.stop()

    # Get image from /ecg-image/
    with st.spinner("📈 Đang tải biểu đồ điện tim..."):
        image_base64 = ""
        if record_id:
            image_api_url = f"https://heartpredict.duckdns.org/ecg-image/?record_id={record_id}"
            image_response = requests.get(image_api_url)
            if image_response.status_code == 200:
                image_base64 = image_response.json().get("ecg_plot_base64", "")
            else:
                st.warning("⚠️ Không lấy được ảnh ECG từ server.")

        # Show ECG image
        st.markdown("### 📈 Biểu đồ điện tim")
        if image_base64:
            # image_bytes = base64.b64decode(image_base64)
            # image = Image.open(io.BytesIO(image_bytes))
            # st.image(image, use_container_width=True, caption="Biểu đồ đồ điện tim")
            zoom_html = f"""
                                <div style="text-align: center;">
                                  <style>
                                    .zoomable-img {{
                                        transition: transform 0.3s;
                                        width: 100%;
                                    }}
                                    .zoomable-img:hover {{
                                        transform: scale(1.5);
                                        z-index: 10;
                                    }}
                                  </style>
                                  <img src="data:image/png;base64,{image_base64}" class="zoomable-img" />
                                </div>
                                """
            st.markdown(zoom_html, unsafe_allow_html=True)
    del image_base64
    gc.collect()