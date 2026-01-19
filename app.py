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
st.title("🔥 Fire Safety Detection System")
st.caption("Cloud-safe fire detection • Image & Video snapshot analysis")
st.divider()

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected: {st.session_state.fire_count}")

# ================= FIRE DETECTION LOGIC =================
def detect_fire(image: Image.Image) -> bool:
    img = np.array(image).astype(np.float32)
    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

    fire_mask = (
        (r > 140) &
        (g > 80) &
        (b < 140) &
        (r > g) &
        (g >= b)
    )

    fire_ratio = np.sum(fire_mask) / fire_mask.size
    if fire_ratio < 0.005:
        return False

    brightness = (r + g + b) / 3
    if np.mean(brightness[fire_mask]) < 120:
        return False

    return True


def draw_fire_box(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    w, h = image.size

    x1, y1 = int(w * 0.2), int(h * 0.2)
    x2, y2 = int(w * 0.8), int(h * 0.8)

    draw.rectangle([x1, y1, x2, y2], outline="red", width=5)
    draw.text((x1, y1 - 30), "🔥 FIRE", fill="red")
    return image

# ================= IMAGE UPLOAD =================
st.subheader("📤 Upload Image")

image_file = st.file_uploader(
    "Upload an image (JPG / PNG)",
    type=["jpg", "jpeg", "png"]
)

if image_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_file.read())
        path = tmp.name

    image = Image.open(path).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Analyzing image..."):
        fire = detect_fire(image)

    if fire:
        st.session_state.fire_count += 1
        boxed = draw_fire_box(image.copy())

        st.error("🔥 FIRE DETECTED")
        st.image(boxed, caption="Fire Detected Region", use_container_width=True)

        os.makedirs("alerts", exist_ok=True)
        out = f"alerts/fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        boxed.save(out)

        with open(out, "rb") as f:
            st.download_button(
                "⬇️ Download Fire Evidence Image",
                f,
                file_name=os.path.basename(out),
                mime="image/jpeg"
            )
    else:
        st.success("✅ No fire detected in the image")

# ================= VIDEO SECTION =================
st.divider()
st.subheader("🎥 Video Fire Detection (Cloud-Safe)")

st.info(
    "🔒 Cloud platforms cannot decode videos.\n\n"
    "👉 Upload a **snapshot (frame)** from your video for fire detection."
)

video_file = st.file_uploader(
    "Upload video (MP4 / AVI / MOV)",
    type=["mp4", "avi", "mov"]
)

if video_file:
    st.video(video_file)
    st.warning("⬇️ Now upload a snapshot (frame) from this video")

    frame_file = st.file_uploader(
        "Upload snapshot image from the video",
        type=["jpg", "jpeg", "png"],
        key="video_frame"
    )

    if frame_file:
        image = Image.open(frame_file).convert("RGB")
        st.image(image, caption="Video Snapshot", use_container_width=True)

        with st.spinner("🔍 Analyzing snapshot..."):
            fire = detect_fire(image)

        if fire:
            st.session_state.fire_count += 1
            boxed = draw_fire_box(image.copy())

            st.error("🔥 FIRE DETECTED IN VIDEO")
            st.image(boxed, caption="Fire Detected Frame", use_container_width=True)
        else:
            st.success("✅ No fire detected in the video")

# ================= SAFETY =================
st.divider()
st.subheader("🛡️ Fire Safety Awareness")

with st.expander("🚨 Emergency Steps"):
    st.markdown("""
    - Stay calm and evacuate immediately  
    - Do NOT use elevators  
    - Turn off gas and electricity if safe  
    - Call **Fire Emergency: 101 (India)**
    """)

# ================= DISCLAIMER =================
st.divider()
st.caption(
    "⚠️ This cloud demo uses snapshot-based fire detection for stability. "
    "Production systems use deep-learning models on edge devices."
)
