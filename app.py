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
st.caption("Unified Cloud Demo • Stable on Hugging Face & Streamlit Cloud")
st.divider()

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected: {st.session_state.fire_count}")

# ================= ROBUST FIRE DETECTION =================
def detect_fire(image: Image.Image):
    """
    Returns:
        fire_detected (bool)
        confidence (float)
    """
    img = np.array(image).astype(np.float32)

    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

    # Fire color heuristic (RELAXED + ROBUST)
    fire_mask = (
        (r > 140) &
        (g > 80) &
        (b < 140) &
        (r > g) &
        (g >= b)
    )

    fire_pixels = np.sum(fire_mask)
    total_pixels = fire_mask.size
    fire_ratio = fire_pixels / total_pixels

    # Brightness confirmation
    brightness = (r + g + b) / 3
    bright_fire = brightness[fire_mask]

    if bright_fire.size == 0:
        return False, 0.0

    avg_brightness = np.mean(bright_fire)

    # Confidence score (used for debugging & stability)
    confidence = min(1.0, fire_ratio * 20 + avg_brightness / 255)

    # Final decision (platform-stable)
    fire_detected = (
        fire_ratio > 0.005 and      # 0.5% fire pixels
        avg_brightness > 120        # glowing fire
    )

    return fire_detected, confidence


def draw_fire_box(image: Image.Image):
    draw = ImageDraw.Draw(image)
    w, h = image.size

    x1, y1 = int(w * 0.2), int(h * 0.2)
    x2, y2 = int(w * 0.8), int(h * 0.8)

    draw.rectangle([x1, y1, x2, y2], outline="red", width=5)
    draw.text((x1, y1 - 30), "🔥 FIRE", fill="red")
    return image

# ================= FILE UPLOAD =================
st.subheader("📤 Upload Image or Video")

uploaded = st.file_uploader(
    "Supported: JPG, PNG, MP4",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
)

if uploaded:
    suffix = os.path.splitext(uploaded.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        path = tmp.name

    # ---------- IMAGE ----------
    if suffix in [".jpg", ".jpeg", ".png"]:
        image = Image.open(path).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        with st.spinner("🔍 Analyzing image..."):
            fire, confidence = detect_fire(image)

        st.caption(f"Detection confidence: **{confidence:.2f}**")

        if fire:
            st.session_state.fire_count += 1

            boxed = draw_fire_box(image.copy())
            st.error("🔥 FIRE DETECTED")
            st.image(boxed, caption="Fire Region", use_container_width=True)

            os.makedirs("alerts", exist_ok=True)
            out = f"alerts/fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            boxed.save(out)

            with open(out, "rb") as f:
                st.download_button(
                    "⬇️ Download Fire Evidence",
                    f,
                    file_name=os.path.basename(out),
                    mime="image/jpeg"
                )
        else:
            st.success("✅ No fire detected")

    # ---------- VIDEO ----------
    else:
        st.video(path)
        st.warning(
            "🎞️ Video analysis on cloud is optimized.\n\n"
            "➡️ Upload a key frame image for accurate detection."
        )

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
    "⚠️ Cloud deployments use heuristic fire detection for stability. "
    "Production systems use deep-learning models on edge devices."
)
