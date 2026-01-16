import streamlit as st
import tempfile
import os
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🔥 Fire Safety Detection System",
    page_icon="🔥",
    layout="wide"
)

# ================= DEMO MODE =================
IS_DEMO_MODE = True  # Cloud-safe demo mode

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
    Cloud-deployed demo | Real AI runs locally / edge
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

# ================= DETECTION MODE =================
if "detection_mode" not in st.session_state:
    st.session_state.detection_mode = "Balanced (Recommended)"

st.sidebar.header("⚙️ Detection Mode")

if st.session_state.admin_logged_in:
    st.session_state.detection_mode = st.sidebar.selectbox(
        "Detection sensitivity (Admin only)",
        ["Balanced (Recommended)", "High Sensitivity", "Low Sensitivity"]
    )
else:
    st.sidebar.info(
        f"🔒 Active Mode: **{st.session_state.detection_mode}**\n\n(Admin controlled)"
    )

st.sidebar.divider()
st.sidebar.markdown("🚨 Emergency: **Fire – 101 (India)**")

# ================= SYSTEM STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected this session: {st.session_state.fire_count}")
st.success(f"⚙️ Active Detection Mode: {st.session_state.detection_mode}")

if IS_DEMO_MODE:
    st.warning("⚠️ DEMO MODE: Cloud-safe simulation enabled")

# ================= FILE UPLOAD =================
st.subheader("📤 Upload Image or Video")

uploaded_file = st.file_uploader(
    "Supported formats: JPG, PNG, MP4, AVI",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
)

if uploaded_file:
    suffix = os.path.splitext(uploaded_file.name)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name

    # Display uploaded content
    if suffix.lower() in [".jpg", ".jpeg", ".png"]:
        st.image(temp_path, caption="Uploaded Image", use_container_width=True)
    else:
        st.video(temp_path)

    # ================= SMART DEMO DETECTION (FIX 3) =================
    st.warning("⚠️ Demo Mode: Intelligent fire simulation")

    fire_keywords = ["fire", "flame", "smoke", "burn", "blaze"]
    filename_lower = uploaded_file.name.lower()

    fire_event_detected = any(keyword in filename_lower for keyword in fire_keywords)

    if fire_event_detected:
        st.session_state.fire_count += 1

        st.error("🔥 FIRE EVENT DETECTED")
        st.caption(
            f"🕒 Detection Time: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}"
        )

        with open(temp_path, "rb") as f:
            st.download_button(
                "⬇️ Download Evidence File",
                f,
                file_name=uploaded_file.name
            )
    else:
        st.success("✅ No fire detected in the uploaded file")

# ================= SAFETY AWARENESS =================
st.divider()
st.subheader("🛡️ Fire Safety Awareness")

with st.expander("🚨 Emergency Steps"):
    st.markdown("""
    - Stay calm and evacuate immediately  
    - Do NOT use elevators  
    - Turn off gas and electricity if safe  
    - Call **Fire Emergency: 101**
    """)

with st.expander("🧯 Fire Prevention Tips"):
    st.markdown("""
    - Do not leave cooking unattended  
    - Keep flammable materials away from heat  
    - Inspect wiring regularly  
    - Install smoke detectors
    """)

# ================= DISCLAIMER =================
st.divider()
st.caption(
    "⚠️ Disclaimer: This cloud deployment demonstrates system workflow only. "
    "Real-time AI inference runs on local or edge devices."
)
