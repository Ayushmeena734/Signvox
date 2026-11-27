# SignVox – Sign Language to Voice Translator

SignVox is a real-time **Indian Sign Language (ISL) to Text and Voice Translator** built with React, FastAPI, MediaPipe, and Scikit-learn. It tracks 21 hand landmarks from a live webcam feed at 60 FPS, classifies gestures using a trained Random Forest model, displays the recognized sign with live confidence scoring, and converts it into speech output.

---

## Features

- **Real-Time 60 FPS Hand Tracking:** Browser-side 21-point hand landmark detection and skeleton overlay using MediaPipe Tasks Vision (`@mediapipe/tasks-vision`).
- **ISL Gesture Classification (`HELLO`):** Wrist-relative coordinate normalization (63 features) classified via a Scikit-learn Random Forest model (`92.7%` test accuracy, `75%` confidence threshold, multi-frame smoothing).
- **Live Translation & Confidence UI:** Displays the recognized sign and real-time confidence percentage across dedicated overlay and output panels.
- **Voice Output:** Button-triggered Text-to-Speech synthesis using the browser's Web Speech API (`SpeechSynthesis`).
- **Full-Stack Architecture:** React + Tailwind CSS frontend communicating with a Python FastAPI REST backend (`/test` and `/predict`).

---

## Technologies Used

### Frontend
- React.js (Vite)
- Tailwind CSS
- MediaPipe Tasks Vision (`@mediapipe/tasks-vision`)
- Web Speech API (`window.speechSynthesis`)

### Backend & Machine Learning
- Python 3.12
- FastAPI & Uvicorn
- Scikit-learn (Random Forest Classifier) & Joblib
- MediaPipe, OpenCV, NumPy & Pandas

---

## Project Structure

```text
Signvox/
├── Backend/
│   ├── dataset/
│   │   ├── signvox_dataset.csv
│   │   ├── amrita_slr_landmarks.csv
│   │   └── amrita_slr_extraction_report.csv
│   ├── models/
│   │   └── hello_detector.pkl
│   ├── collect_data.py          # Webcam tool to record 30-frame normalized gesture samples
│   ├── extract_landmarks.py     # Batch landmark extractor for external sign videos
│   ├── hand_detection.py        # Standalone MediaPipe hand-tracking test script
│   ├── hand_landmarker.task     # MediaPipe HandLandmarker model asset
│   ├── main.py                  # FastAPI server (/test, /predict)
│   ├── requirements.txt         # Python dependencies
│   ├── test_webcam.py           # Standalone OpenCV webcam inference test
│   └── train_model.py           # Random Forest training & evaluation script
│
├── Frontend/
│   ├── public/
│   │   └── hand_landmarker.task # Local MediaPipe asset for smooth browser tracking
│   ├── src/
│   │   ├── assets/
│   │   ├── component/
│   │   │   ├── Camera.jsx
│   │   │   ├── DetectionOverlay.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── ModeSelector.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── TextToSign.jsx
│   │   │   └── TranslationOutput.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── .gitignore
└── README.md