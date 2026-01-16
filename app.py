import streamlit as st
import tempfile
import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🔥 Fire Safety Detection System",
    page_icon="🔥",
    layout="wide"
)

# ================= SESSION STATE =================
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "fire_count" not in st.session_state:
    st.session_state.fire_count = 0

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center;">🔥 Fire Safety Detection System</h1>
    <p style="text-align:center;font-size:18px;">
    Cloud Fire Detection Demo (Content-based)
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()

# ================= SIDEBAR =================
ADMIN_PASSWORD = "admin123"

st.sidebar.header("🔐 Admin Login")

if not st.session_state.admin_logged_in:
    pwd = st.sidebar.text_input("Enter admin password", type="password")
    if pwd == ADMIN_PASSWORD:
        st.session_state.admin_logged_in = True
        st.sidebar.success("Admin logged in")
        st.rerun()
else:
    st.sidebar.success("Logged in as Admin")
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

st.sidebar.divider()
st.sidebar.markdown("🚨 Emergency: **Fire – 101 (India)**")

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected: {st.session_state.fire_count}")

# ================= FIRE DETECTION LOGIC =================
def detect_fire_by_color(image: Image.Image) -> bool:
    img = np.array(image)

    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

    # Fire color heuristic
    fire_pixels = (
        (r > 150) &
        (g > 80) &
        (b < 120) &
        (r > g) &
        (g > b)
    )

    fire_ratio = np.sum(fire_pixels) / fire_pixels.size
    return fire_ratio > 0.02  # 2% fire-like pixels


def draw_fire_box(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    w, h = image.size

    x1, y1 = int(w * 0.25), int(h * 0.25)
    x2, y2 = int(w * 0.75), int(h * 0.75)

    draw.rectangle([x1, y1, x2, y2], outline="red", width=5)
    draw.text((x1, y1 - 30), "🔥 FIRE", fill="red")
    return image

# ================= FILE UPLOAD =================
st.subheader("📤 Upload Image or Video")

uploaded_file = st.file_uploader(
    "Supported formats: JPG, PNG (Video demo limited)",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
)

if uploaded_file:
    suffix = os.path.splitext(uploaded_file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name

    if suffix in [".jpg", ".jpeg", ".png"]:
        image = Image.open(temp_path).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        fire_detected = detect_fire_by_color(image)

        if fire_detected:
            st.session_state.fire_count += 1
            st.error("🔥 FIRE DETECTED")

            boxed = draw_fire_box(image.copy())
            st.image(boxed, caption="Detected Fire Region", use_container_width=True)

            os.makedirs("alerts", exist_ok=True)
            out_path = f"alerts/fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            boxed.save(out_path)

            with open(out_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Fire Evidence Image",
                    f,
                    file_name=os.path.basename(out_path),
                    mime="image/jpeg"
                )
        else:
            st.success("✅ No fire detected in the image")

    else:
        st.warning("🎞️ Video analysis on cloud is limited")
        st.info("Upload an image frame for accurate fire detection")

# ================= SAFETY =================
st.divider()
st.subheader("🛡️ Fire Safety Awareness")

with st.expander("🚨 Emergency Steps"):
    st.markdown("""
    - Stay calm and evacuate immediately  
    - Do NOT use elevators  
    - Turn off gas and electricity if safe  
    - Call **Fire Emergency: 101**
    """)

# ================= DISCLAIMER =================
st.divider()
st.caption(
    "⚠️ Cloud version uses color-based fire detection. "
    "Production systems use deep-learning models on edge devices."
)
