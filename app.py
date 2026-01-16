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

if "detection_mode" not in st.session_state:
    st.session_state.detection_mode = "Balanced (Recommended)"

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center;">🔥 Fire Safety Detection System</h1>
    <p style="text-align:center;font-size:18px;">
    Cloud Demo • Visual Fire Detection • Safety-First Design
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

# ================= STATUS =================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected this session: {st.session_state.fire_count}")
st.success(f"⚙️ Active Detection Mode: {st.session_state.detection_mode}")

if IS_DEMO_MODE:
    st.warning("⚠️ DEMO MODE: Cloud-safe fire detection simulation")

# ================= FIRE BOX FUNCTION =================
def draw_demo_fire_box(image_path):
    img = cv2.imread(image_path)
    h, w, _ = img.shape

    x1, y1 = int(w * 0.25), int(h * 0.25)
    x2, y2 = int(w * 0.75), int(h * 0.75)

    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
    cv2.putText(
        img,
        "🔥 FIRE",
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )
    return img

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

    # ================= SMART DEMO DETECTION =================
    fire_keywords = ["fire", "flame", "smoke", "burn", "blaze"]
    filename_lower = uploaded_file.name.lower()

    fire_event_detected = any(keyword in filename_lower for keyword in fire_keywords)

    if fire_event_detected:
        st.session_state.fire_count += 1

        st.error("🔥 FIRE EVENT DETECTED")
        st.caption(
            f"🕒 Detection Time: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}"
        )

        # Draw fire bounding box (image only)
        if suffix.lower() in [".jpg", ".jpeg", ".png"]:
            boxed_img = draw_demo_fire_box(temp_path)

            st.image(
                boxed_img,
                caption="Detected Fire Region (Demo Visualization)",
                use_container_width=True
            )

            os.makedirs("alerts", exist_ok=True)
            out_path = f"alerts/fire_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(out_path, boxed_img)

            with open(out_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Fire Evidence Image",
                    f,
                    file_name=os.path.basename(out_path),
                    mime="image/jpeg"
                )
        else:
            st.info("🎞️ Fire detected in video (visual box shown for images only)")

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

