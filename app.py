import streamlit as st
import tempfile
import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw
import imageio

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
st.caption("Cloud-safe fire detection • Image & Video supported")
st.divider()

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected: {st.session_state.fire_count}")

# ================= FIRE DETECTION =================
def detect_fire(image: Image.Image):
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
    "Supported formats: JPG, PNG, MP4, AVI, MOV",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
)

if uploaded:
    suffix = os.path.splitext(uploaded.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        path = tmp.name

    # ================= IMAGE =================
    if suffix in [".jpg", ".jpeg", ".png"]:
        image = Image.open(path).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        with st.spinner("🔍 Analyzing image..."):
            fire = detect_fire(image)

        if fire:
            st.session_state.fire_count += 1
            boxed = draw_fire_box(image.copy())

            st.error("🔥 FIRE DETECTED")
            st.image(boxed, caption="Fire Detected", use_container_width=True)

            os.makedirs("alerts", exist_ok=True)
            out = f"alerts/fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            boxed.save(out)

            with open(out, "rb") as f:
                st.download_button(
                    "⬇️ Download Fire Image",
                    f,
                    file_name=os.path.basename(out),
                    mime="image/jpeg"
                )
        else:
            st.success("✅ No fire detected")

    # ================= VIDEO =================
    else:
        st.video(path)

        st.spinner("🔍 Analyzing video for fire...")

        reader = imageio.get_reader(path)
        fps = reader.get_meta_data().get("fps", 10)

        fire_found = False
        detected_frame = None

        for i, frame in enumerate(reader):
            # Sample 1 frame per second
            if i % int(fps) != 0:
                continue

            image = Image.fromarray(frame).convert("RGB")
            if detect_fire(image):
                fire_found = True
                detected_frame = draw_fire_box(image)
                break

        reader.close()

        if fire_found:
            st.session_state.fire_count += 1
            st.error("🔥 FIRE DETECTED IN VIDEO")
            st.image(detected_frame, caption="Fire Detected Frame", use_container_width=True)

            os.makedirs("alerts", exist_ok=True)
            out = f"alerts/video_fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            detected_frame.save(out)

            with open(out, "rb") as f:
                st.download_button(
                    "⬇️ Download Detected Frame",
                    f,
                    file_name=os.path.basename(out),
                    mime="image/jpeg"
                )
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
    "⚠️ Cloud deployment uses optimized fire detection. "
    "Production systems use deep learning models on edge devices."
)

