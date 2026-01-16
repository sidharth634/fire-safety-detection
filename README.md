🔥 Fire & Smoke Detection using YOLOv8


📌 Project Overview

This project implements a real-time fire and smoke detection system using YOLOv8.
It detects fire-related events from images, videos, and webcam streams and triggers alerts for early safety monitoring.


🎯 Problem Statement


Traditional fire detection systems based on sensors can be slow or limited.
This project uses computer vision to detect fire and smoke visually for faster and broader coverage.

🧠 Solution Approach


Classical Computer Vision (OpenCV)

Color-based fire detection using HSV

Observed limitations like false positives

Deep Learning (YOLOv8)

Trained a custom object detection model for fire and smoke

Used GPU acceleration (CUDA) for faster training

Achieved accurate detection with fewer false positives

Real-Time Deployment

Image detection

Video detection

Webcam-based real-time fire event alerts

⚙️ Tech Stack


Python

OpenCV

YOLOv8 (Ultralytics)

PyTorch

CUDA (GPU Acceleration)


🚀 Features


Fire & smoke detection in images

Real-time video and webcam inference

Alert system for fire-related events

Industry-style fire-event logic (fire OR smoke → alert)



▶️ How to Run


Install dependencies

pip install -r requirements.txt


Train the model

python train.py


Run image detection

python detect_yolo.py


Run video detection

python detect_video.py


Run webcam fire alert

python detect_webcam_alert.py

📈 Key Learnings


Limitations of rule-based computer vision

Importance of dataset quality

GPU-accelerated deep learning workflows

Real-world deployment challenges

📌 Future Improvements


Improve dataset labeling

Merge fire & smoke into a single fire-event class

Add sound/email alerts

Deploy as a web or mobile application


