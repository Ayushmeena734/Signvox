import cv2
import mediapipe as mp
import numpy as np
import joblib
import math
import pandas as pd

from pathlib import Path
from collections import deque, Counter


# --------------------------------
# 1. Load trained model
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "models" / "hello_detector.pkl"

saved_data = joblib.load(MODEL_FILE)

model = saved_data["model"]
feature_columns = saved_data["feature_columns"]
class_labels = list(model.classes_)
hello_index = class_labels.index("HELLO")

CONFIDENCE_THRESHOLD = 0.75

print("HELLO detector loaded successfully!")
print(f"Confidence threshold set to: {CONFIDENCE_THRESHOLD:.0%}")


# --------------------------------
# 2. MediaPipe setup
# --------------------------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)


# --------------------------------
# 3. Landmark normalization
# --------------------------------

def normalize_landmarks(hand_landmarks):

    coordinates = []

    wrist = hand_landmarks.landmark[0]

    for landmark in hand_landmarks.landmark:

        x = landmark.x - wrist.x
        y = landmark.y - wrist.y
        z = landmark.z - wrist.z

        coordinates.append([x, y, z])

    scale = max(
        math.sqrt(x*x + y*y + z*z)
        for x, y, z in coordinates
    )

    if scale == 0:
        scale = 1

    normalized = []

    for x, y, z in coordinates:

        normalized.extend([
            x / scale,
            y / scale,
            z / scale
        ])

    return normalized


# --------------------------------
# 4. Prediction smoothing
# --------------------------------

prediction_history = deque(maxlen=10)


# --------------------------------
# 5. Start webcam
# --------------------------------

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():

    raise RuntimeError("Could not open webcam.")

print("Webcam opened successfully!")
print("Show your hand to test the model.")
print("Press Q to quit.")


try:

    while cap.isOpened():

        success, frame = cap.read()

        if not success:
            print("Unable to read webcam frame.")
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(rgb_frame)

        display_text = "Show your hand"
        color = (0, 0, 255)

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = normalize_landmarks(hand)

            input_data = pd.DataFrame(
                [landmarks],
                columns=feature_columns
            )

            probabilities = model.predict_proba(input_data)[0]
            hello_confidence = probabilities[hello_index]

            if hello_confidence >= CONFIDENCE_THRESHOLD:
                frame_prediction = "HELLO"
            else:
                frame_prediction = "NOT_HELLO"

            prediction_history.append(frame_prediction)

            stable_prediction = Counter(
                prediction_history
            ).most_common(1)[0][0]

            if stable_prediction == "HELLO":

                display_text = f"HELLO ({hello_confidence:.0%})"
                color = (0, 255, 0)

            else:

                display_text = f"NOT HELLO ({hello_confidence:.0%})"
                color = (0, 165, 255)

        else:

            prediction_history.clear()

        cv2.putText(
            frame,
            display_text,
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            color,
            3
        )

        cv2.imshow(
            "SignVox - HELLO Recognition",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

finally:

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

    print("Webcam testing stopped.")