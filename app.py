import streamlit as st
from ultralytics import YOLO
import tempfile
import os
import cv2
import numpy as np
from datetime import datetime

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Fire Safety Detection System",
    page_icon="🔥",
    layout="wide"
)

# ================== SESSION STATE ==================
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "fire_count" not in st.session_state:
    st.session_state.fire_count = 0

if "last_fire_id" not in st.session_state:
    st.session_state.last_fire_id = None

# 🔐 Detection mode stored in session (ADMIN controlled)
if "detection_mode" not in st.session_state:
    st.session_state.detection_mode = "Balanced (Recommended)"

# ================== HEADER ==================
st.markdown(
    """
    <h1 style='text-align:center;'>🔥 Fire Safety Detection System</h1>
    <p style='text-align:center;font-size:18px;'>
    AI-powered fire & smoke detection (safety-first, admin-controlled)
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()

# ================== SIDEBAR ==================
ADMIN_PASSWORD = "admin123"
st.sidebar.header("🔐 Admin Access")

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

# ================== DETECTION MODE (ADMIN ONLY) ==================
st.sidebar.divider()
st.sidebar.header("⚙️ Detection Mode")

if st.session_state.admin_logged_in:
    st.session_state.detection_mode = st.sidebar.selectbox(
        "Set detection sensitivity (Admin only)",
        ["Balanced (Recommended)", "High Sensitivity (Early Warning)", "Low Sensitivity (Strict)"],
        index=["Balanced (Recommended)", "High Sensitivity (Early Warning)", "Low Sensitivity (Strict)"]
        .index(st.session_state.detection_mode)
    )
else:
    st.sidebar.info(
        f"🔒 Detection Mode: **{st.session_state.detection_mode}**\n\n"
        "Only admin can change this."
    )

# Map detection mode → confidence
if st.session_state.detection_mode == "High Sensitivity (Early Warning)":
    confidence = 0.2
elif st.session_state.detection_mode == "Low Sensitivity (Strict)":
    confidence = 0.6
else:
    confidence = 0.4

st.sidebar.markdown("""
**Detection Logic**
- Fire OR Smoke → FIRE EVENT
- Safety-first configuration
""")

st.sidebar.divider()
st.sidebar.markdown("🚨 Emergency: **Fire – 101 (India)**")

# ================== LOAD MODEL ==================
@st.cache_resource
def load_model():
    return YOLO("models/fire_model.pt")



model = load_model()

# ================== STATUS ==================
st.subheader("📊 System Status")
st.info(f"🔥 Total fire events detected this session: {st.session_state.fire_count}")
st.success(f"⚙️ Active Detection Mode: {st.session_state.detection_mode}")

# ================== FILE UPLOAD ==================
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

    fire_event = False
    annotated = None
    fire_id = None

    with st.spinner("🔍 Analyzing input..."):

        if suffix.lower() in [".jpg", ".jpeg", ".png"]:
            r = model.predict(temp_path, conf=confidence)[0]
            frame = cv2.imread(temp_path)

            if r.boxes is not None and len(r.boxes) > 0:
                annotated = frame.copy()
                for box in r.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(
                        annotated, "FIRE", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2
                    )
                fire_event = True

        else:
            cap = cv2.VideoCapture(temp_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                r = model(frame, conf=confidence)[0]
                if r.boxes is not None and len(r.boxes) > 0:
                    annotated = frame.copy()
                    for box in r.boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.putText(
                            annotated, "FIRE", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2
                        )
                    fire_event = True
                    break
            cap.release()

    if fire_event:
        fire_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        if st.session_state.last_fire_id != fire_id:
            st.session_state.fire_count += 1
            st.session_state.last_fire_id = fire_id

        os.makedirs("alerts", exist_ok=True)
        img_path = f"alerts/fire_{fire_id}.jpg"
        cv2.imwrite(img_path, annotated)

        st.error("🔥 FIRE EVENT DETECTED")
        st.image(annotated, channels="BGR", use_container_width=True)

        with open(img_path, "rb") as f:
            st.download_button(
                "⬇️ Download Detected Image",
                f,
                file_name=os.path.basename(img_path),
                mime="image/jpeg"
            )
    else:
        st.success("✅ No fire detected")

# ================== LIVE WEBCAM (ADMIN ONLY) ==================
if st.session_state.admin_logged_in:
    st.divider()
    st.subheader("🎥 Live Webcam Fire Detection (Admin Only)")

    start = st.button("▶ Start Webcam Monitoring")
    stop = st.button("⏹ Stop Webcam")

    frame_box = st.empty()

    if start:
        cap = cv2.VideoCapture(0)
        frame_count = 0
        st.info("Webcam monitoring started (optimized mode)")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or stop:
                break

            frame_count += 1
            if frame_count % 10 != 0:
                continue

            r = model(frame, conf=confidence)[0]
            frame_box.image(frame, channels="BGR")

            if r.boxes is not None and len(r.boxes) > 0:
                fire_id = datetime.now().strftime("%Y%m%d_%H%M%S")

                if st.session_state.last_fire_id != fire_id:
                    st.session_state.fire_count += 1
                    st.session_state.last_fire_id = fire_id

                annotated = frame.copy()
                for box in r.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(
                        annotated, "FIRE", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2
                    )

                os.makedirs("alerts", exist_ok=True)
                img_path = f"alerts/webcam_fire_{fire_id}.jpg"
                cv2.imwrite(img_path, annotated)

                st.error("🔥 FIRE DETECTED — Screenshot Captured")
                st.image(annotated, channels="BGR", use_container_width=True)

                with open(img_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Webcam Snapshot",
                        f,
                        file_name=os.path.basename(img_path),
                        mime="image/jpeg"
                    )
                break

        cap.release()
        frame_box.empty()

# ================== DISCLAIMER ==================
st.divider()
st.caption(
    "⚠️ Disclaimer: This system assists early fire detection and must not replace certified fire alarm systems."
)


