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
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "fire_count" not in st.session_state:
    st.session_state.fire_count = 0

if "history" not in st.session_state:
    st.session_state.history = []

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center;"> Fire Safety Detection System</h1>
    <p style="text-align:center;font-size:18px;">
    Cloud-Safe | Image & Video Snapshot Fire Detection | Safety-First Design
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
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged_in = False
        st.rerun()

st.sidebar.divider()
st.sidebar.markdown("🚨 **Fire Emergency (India): 101**")

# ================= DASHBOARD =================
st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("🔥 Fire Events", st.session_state.fire_count)
col2.metric("📁 Files Analyzed", len(st.session_state.history))
col3.metric("🟢 System Status", "Active")

st.divider()

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

# ================= MAIN TABS =================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🖼 Image Detection", "🎥 Video Detection", "📂 History", "🛡 Safety"]
)

# ================= IMAGE DETECTION =================
with tab1:
    st.subheader("🖼 Image Fire Detection")

    img_file = st.file_uploader(
        "Upload image (JPG / PNG)",
        type=["jpg", "jpeg", "png"],
        key="image_upload"
    )

    if img_file:
        image = Image.open(img_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        with st.spinner("🔍 Analyzing image..."):
            fire = detect_fire(image)

        timestamp = datetime.now().strftime("%d %b %Y, %H:%M:%S")

        if fire:
            boxed = draw_fire_box(image.copy())
            st.error("🔥 FIRE DETECTED")
            st.image(boxed, use_container_width=True)

            st.session_state.fire_count += 1
            st.session_state.history.append(
                {"time": timestamp, "type": "Image", "result": "Fire"}
            )

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
            st.session_state.history.append(
                {"time": timestamp, "type": "Image", "result": "No Fire"}
            )

# ================= VIDEO DETECTION =================
with tab2:
    st.subheader("🎥 Video Fire Detection (Snapshot-Based)")

    st.info(
        "🔒 Cloud platforms cannot decode videos.\n\n"
        "👉 Upload a **snapshot (frame)** from your video for detection."
    )

    video_file = st.file_uploader(
        "Upload video (MP4 / AVI / MOV)",
        type=["mp4", "avi", "mov"],
        key="video_upload"
    )

    if video_file:
        st.video(video_file)

        frame_file = st.file_uploader(
            "Upload snapshot image from this video",
            type=["jpg", "jpeg", "png"],
            key="video_frame_upload"
        )

        if frame_file:
            image = Image.open(frame_file).convert("RGB")
            st.image(image, caption="Video Snapshot", use_container_width=True)

            with st.spinner("🔍 Analyzing snapshot..."):
                fire = detect_fire(image)

            timestamp = datetime.now().strftime("%d %b %Y, %H:%M:%S")

            if fire:
                boxed = draw_fire_box(image.copy())
                st.error("🔥 FIRE DETECTED IN VIDEO")
                st.image(boxed, use_container_width=True)

                st.session_state.fire_count += 1
                st.session_state.history.append(
                    {"time": timestamp, "type": "Video", "result": "Fire"}
                )
            else:
                st.success("✅ No fire detected in video")
                st.session_state.history.append(
                    {"time": timestamp, "type": "Video", "result": "No Fire"}
                )

# ================= HISTORY =================
with tab3:
    st.subheader("📂 Detection History")

    if not st.session_state.history:
        st.info("No detections yet.")
    else:
        for h in reversed(st.session_state.history):
            st.markdown(
                f"• **{h['time']}** | {h['type']} | "
                f"{'🔥 Fire' if h['result']=='Fire' else '✅ No Fire'}"
            )

        if st.session_state.admin_logged_in:
            if st.button("🗑 Clear History (Admin)"):
                st.session_state.history.clear()
                st.session_state.fire_count = 0
                st.rerun()

# ================= SAFETY =================
with tab4:
    st.subheader("🛡 Fire Safety Awareness")

    with st.expander("🚨 Emergency Steps"):
        st.markdown("""
        - Stay calm and evacuate immediately  
        - Do NOT use elevators  
        - Turn off gas and electricity if safe  
        - Call **Fire Emergency: 101 (India)**
        """)

    with st.expander("🧯 Fire Prevention Tips"):
        st.markdown("""
        - Never leave cooking unattended  
        - Keep flammable items away from heat  
        - Inspect wiring regularly  
        - Install smoke detectors
        """)

# ================= DISCLAIMER =================
st.divider()
st.caption(
    "⚠️ Disclaimer: This system assists early fire detection and does NOT "
    "replace certified fire alarm systems. Cloud version uses snapshot-based analysis."
)

