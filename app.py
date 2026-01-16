import streamlit as st
import tempfile
import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🔥 Fire Safety Detection System",
    page_icon="🔥",
    layout="wide"
)

# ================= SESSION STATE =================
if "fire_count" not in st.session_state:
    st.session_state.fire_count = 0

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center;">🔥 Fire Safety Detection System</h1>
    <p style="text-align:center;font-size:18px;">
    Cloud Demo • Multi-Stage Fire Detection
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected: {st.session_state.fire_count}")

# ================= ADVANCED FIRE DETECTION =================
def detect_fire_advanced(image: Image.Image) -> bool:
    img = np.array(image).astype(np.float32)

    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

    # 1️⃣ Fire color condition
    fire_mask = (
        (r > 160) &
        (g > 90) &
        (b < 120) &
        (r > g) &
        (g > b)
    )

    fire_pixel_ratio = np.sum(fire_mask) / fire_mask.size
    if fire_pixel_ratio < 0.01:  # at least 1%
        return False

    # 2️⃣ Brightness check
    brightness = (r + g + b) / 3
    if np.mean(brightness[fire_mask]) < 150:
        return False

    # 3️⃣ Connectivity (cluster check)
    fire_rows = np.any(fire_mask, axis=1)
    fire_cols = np.any(fire_mask, axis=0)

    height_ratio = np.sum(fire_rows) / fire_rows.size
    width_ratio = np.sum(fire_cols) / fire_cols.size

    if height_ratio < 0.15 or width_ratio < 0.15:
        return False

    return True


def draw_fire_box(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    w, h = image.size

    x1, y1 = int(w * 0.2), int(h * 0.2)
    x2, y2 = int(w * 0.8), int(h * 0.8)

    draw.rectangle([x1, y1, x2, y2], outline="red", width=5)
    draw.text((x1, y1 - 30), "🔥 FIRE DETECTED", fill="red")
    return image

# ================= FILE UPLOAD =================
st.subheader("📤 Upload Image")

uploaded_file = st.file_uploader(
    "Upload image (JPG / PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name

    image = Image.open(temp_path).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Analyzing image..."):
        fire_detected = detect_fire_advanced(image)

    if fire_detected:
        st.session_state.fire_count += 1
        st.error("🔥 FIRE CONFIRMED")

        boxed = draw_fire_box(image.copy())
        st.image(boxed, caption="Fire Region", use_container_width=True)

        os.makedirs("alerts", exist_ok=True)
        out_path = f"alerts/fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        boxed.save(out_path)

        with open(out_path, "rb") as f:
            st.download_button(
                "⬇️ Download Fire Evidence",
                f,
                file_name=os.path.basename(out_path),
                mime="image/jpeg"
            )
    else:
        st.success("✅ No fire detected")

# ================= DISCLAIMER =================
st.divider()
st.caption(
    "⚠️ Cloud demo uses heuristic fire detection. "
    "Production systems use deep learning (YOLO) on edge devices."
            )
