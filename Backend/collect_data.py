
import cv2
import mediapipe as mp
import csv
import os
import time
import math

from pathlib import Path


# -------------------------------
# 1. Dataset Configuration
# -------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "dataset"

DATASET_DIR.mkdir(exist_ok=True)

CSV_FILE = DATASET_DIR / "signvox_dataset.csv"

SAMPLES_PER_SIGN = 100
FRAMES_PER_SAMPLE = 30


# -------------------------------
# 2. CSV Columns
# -------------------------------

columns = ["sample_id", "label", "frame"]

for i in range(21):
    columns.extend([
        f"x{i}",
        f"y{i}",
        f"z{i}"
    ])


# Create CSV if it doesn't exist

if not CSV_FILE.exists():

    with open(CSV_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(columns)


# -------------------------------
# 3. MediaPipe Setup
# -------------------------------

mp_hands = mp.solutions.hands

mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)


# -------------------------------
# 4. Landmark Normalization
# -------------------------------

def normalize_landmarks(hand_landmarks):

    coordinates = []

    # Get wrist coordinates (landmark 0)

    wrist = hand_landmarks.landmark[0]

    for landmark in hand_landmarks.landmark:

        x = landmark.x - wrist.x
        y = landmark.y - wrist.y
        z = landmark.z - wrist.z

        coordinates.append([x, y, z])

    # Calculate scale

    scale = max(
        math.sqrt(x*x + y*y + z*z)
        for x, y, z in coordinates
    )

    if scale == 0:
        scale = 1

    # Normalize coordinates

    normalized = []

    for x, y, z in coordinates:

        normalized.extend([
            x / scale,
            y / scale,
            z / scale
        ])

    return normalized


# -------------------------------
# 5. Get Existing Samples
# -------------------------------

def get_existing_samples(label):

    sample_ids = set()

    with open(CSV_FILE, "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["label"] == label:

                sample_ids.add(row["sample_id"])

    return len(sample_ids)


# -------------------------------
# 6. Start Data Collection
# -------------------------------

label = input("Enter sign name (e.g. HELLO): ").strip().upper()

if not label:
    raise ValueError("Sign name cannot be empty.")

completed_samples = get_existing_samples(label)

print("Existing samples:", completed_samples)

if completed_samples >= SAMPLES_PER_SIGN:
    print("Target already completed!")
    raise SystemExit


# Open laptop webcam

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam. Check camera index.")
print("Webcam opened successfully!")

ret, test_frame = cap.read()

print("Frame captured:", ret)


print("\nSignVox Dataset Collection Started")
print("Press SPACE to record a sample")
print("Press Q to quit")


# -------------------------------
# 7. Recording Variables
# -------------------------------

recording = False

current_frames = []

sample_number = completed_samples


# -------------------------------
# 8. Main Webcam Loop
# -------------------------------

try:

    with open(CSV_FILE, "a", newline="") as file:

        writer = csv.writer(file)

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

            hand_detected = False

            if results.multi_hand_landmarks:

                hand_detected = True

                hand = results.multi_hand_landmarks[0]

                mp_draw.draw_landmarks(
                    frame,
                    hand,
                    mp_hands.HAND_CONNECTIONS
                )

                # Collect frames only while recording

                if recording:

                    landmarks = normalize_landmarks(hand)

                    current_frames.append(landmarks)

            # -------------------------------
            # Display Information
            # -------------------------------

            cv2.putText(
                frame,
                f"Sign: {label}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Samples: {sample_number}/{SAMPLES_PER_SIGN}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            if recording:

                cv2.putText(
                    frame,
                    f"Recording: {len(current_frames)}/{FRAMES_PER_SAMPLE}",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

            elif hand_detected:

                cv2.putText(
                    frame,
                    "Press SPACE to record",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            else:

                cv2.putText(
                    frame,
                    "Show your hand",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("SignVox Dataset Collection", frame)

            # -------------------------------
            # Keyboard Controls
            # -------------------------------

            key = cv2.waitKey(1) & 0xFF

            # Quit

            if key == ord("q"):
                break

            # Start recording

            if key == 32 and not recording:

                if hand_detected:

                    recording = True

                    current_frames = []

                    print("\nRecording new sample...")

                else:

                    print("Please show your hand first.")

            # -------------------------------
            # Save Complete Sample
            # -------------------------------

            if recording and len(current_frames) >= FRAMES_PER_SAMPLE:

                sample_number += 1

                sample_id = f"{label}_{sample_number:03d}"

                for frame_number, coordinates in enumerate(
                    current_frames, start=1
                ):

                    writer.writerow([
                        sample_id,
                        label,
                        frame_number,
                        *coordinates
                    ])

                file.flush()

                print(
                    f"Saved {sample_id} "
                    f"({sample_number}/{SAMPLES_PER_SIGN})"
                )

                recording = False

                current_frames = []

            # Stop after reaching target

            if sample_number >= SAMPLES_PER_SIGN:

                print("\nTarget of 100 samples completed!")

                break

finally:

    cap.release()

    cv2.destroyAllWindows()

    hands.close()

    print("\nDataset collection stopped.")
