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

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ================= THEME TOGGLE =================
st.sidebar.header("🎨 Theme")
theme_toggle = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=(st.session_state.theme == "Dark")
)

st.session_state.theme = "Dark" if theme_toggle else "Light"

# Apply theme
if st.session_state.theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #0E1117; color: white; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center;">🔥 Fire Safety Detection System</h1>
    <p style="text-align:center;font-size:18px;">
    Cloud-Safe | Image & Video Snapshot Fire Detection
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
col3.metric("🎨 Theme", st.session_state.theme)

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
    return np.mean(brightness[fire_mask]) > 120


def draw_fire_box(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    w, h = image.size
    draw.rectangle(
        [int(w*0.2), int(h*0.2), int(w*0.8), int(h*0.8)],
        outline="red", width=5
    )
    draw.text((int(w*0.2), int(h*0.2)-30), "🔥 FIRE", fill="red")
    return image

# ================= TABS =================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🖼 Image Detection", "🎥 Video Detection", "📂 History", "🛡 Safety"]
)

# ================= IMAGE =================
with tab1:
    img_file = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png"]
    )

    if img_file:
        image = Image.open(img_file).convert("RGB")
        st.image(image, use_container_width=True)

        fire = detect_fire(image)
        time_now = datetime.now().strftime("%d %b %Y, %H:%M:%S")

        if fire:
            boxed = draw_fire_box(image.copy())
            st.error("🔥 FIRE DETECTED")
            st.image(boxed, use_container_width=True)

            st.session_state.fire_count += 1
            st.session_state.history.append(
                {"time": time_now, "type": "Image", "result": "Fire"}
            )
        else:
            st.success("✅ No fire detected")
            st.session_state.history.append(
                {"time": time_now, "type": "Image", "result": "No Fire"}
            )

# ================= VIDEO =================
with tab2:
    st.info("Upload a snapshot image from the video for detection.")

    frame = st.file_uploader(
        "Upload video snapshot",
        type=["jpg", "jpeg", "png"]
    )

    if frame:
        image = Image.open(frame).convert("RGB")
        st.image(image, use_container_width=True)

        fire = detect_fire(image)
        time_now = datetime.now().strftime("%d %b %Y, %H:%M:%S")

        if fire:
            boxed = draw_fire_box(image.copy())
            st.error("🔥 FIRE DETECTED IN VIDEO")
            st.image(boxed, use_container_width=True)

            st.session_state.fire_count += 1
            st.session_state.history.append(
                {"time": time_now, "type": "Video", "result": "Fire"}
            )
        else:
            st.success("✅ No fire detected")
            st.session_state.history.append(
                {"time": time_now, "type": "Video", "result": "No Fire"}
            )

# ================= HISTORY =================
with tab3:
    st.subheader("📂 Detection History")

    if not st.session_state.history:
        st.info("📭 No detections yet.")
    else:
        for h in reversed(st.session_state.history):
            st.markdown(
                f"• **{h['time']}** | {h['type']} | "
                f"{'🔥 Fire' if h['result']=='Fire' else '✅ No Fire'}"
            )

    if st.session_state.admin_logged_in:
        if st.button("🗑 Clear History (Admin Only)"):
            st.session_state.history.clear()
            st.session_state.fire_count = 0
            st.success("History cleared successfully")
            st.rerun()

# ================= SAFETY =================
with tab4:
    st.markdown("""
    ### 🚨 Emergency Steps
    - Evacuate immediately  
    - Do not use elevators  
    - Call **101**

    ### 🧯 Prevention
    - Avoid unattended cooking  
    - Check wiring  
    - Install smoke detectors
    """)

# ================= DISCLAIMER =================
st.divider()
st.caption(
    "⚠️ This system assists early fire detection and does NOT replace certified fire alarm systems."
)
