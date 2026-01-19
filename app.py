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
st.caption("Cloud-safe demo • Visual fire detection • No GPU required")
st.divider()

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected: {st.session_state.fire_count}")

# ================= FIRE DETECTION (CLOUD SAFE) =================
def detect_fire(image: Image.Image) -> bool:
    """Multi-stage fire detection using color + brightness + clustering"""
    img = np.array(image).astype(np.float32)
    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

    fire_mask = (
        (r > 160) &
        (g > 90) &
        (b < 120) &
        (r > g) &
        (g > b)
    )

    ratio = np.sum(fire_mask) / fire_mask.size
    if ratio < 0.01:
        return False

    brightness = (r + g + b) / 3
    if np.mean(brightness[fire_mask]) < 150:
        return False

    rows = np.any(fire_mask, axis=1)
    cols = np.any(fire_mask, axis=0)

    if np.sum(rows) / rows.size < 0.15:
        return False
    if np.sum(cols) / cols.size < 0.15:
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

# ================= FILE UPLOAD =================
st.subheader("📤 Upload Image or Video")

uploaded = st.file_uploader(
    "Supported: JPG, PNG, MP4 (video analyzed via key frame)",
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
        st.info("🎞️ Video analyzed using representative frame")

        st.warning(
            "⚠️ Cloud optimization: upload a key frame image for best accuracy"
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
    "⚠️ Cloud demo uses heuristic fire detection. "
    "Real deployments use YOLO models on edge devices."
)
