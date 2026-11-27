import cv2
import mediapipe as mp
import numpy as np
import time

from pathlib import Path

# Model path
MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Hand connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


def start_hand_detection():

    options = HandLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=str(MODEL_PATH)
        ),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2
    )

    # Open webcam
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera could not be opened!")
        return

    start_time = time.perf_counter()

    with HandLandmarker.create_from_options(options) as landmarker:

        while True:

            success, frame = camera.read()

            if not success:
                print("Unable to read camera frame")
                break

            # Mirror camera
            frame = cv2.flip(frame, 1)

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            # Create MediaPipe image
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # Timestamp in milliseconds
            timestamp = int(
                (time.perf_counter() - start_time) * 1000
            )

            # Detect hands
            result = landmarker.detect_for_video(
                mp_image, timestamp
            )

            # Process detected hands
            if result.hand_landmarks:

                for hand in result.hand_landmarks:

                    # Extract X, Y, Z coordinates
                    landmarks = np.array([
                        [point.x, point.y, point.z]
                        for point in hand
                    ], dtype=np.float32)

                    print("Landmark shape:", landmarks.shape)

                    height, width, _ = frame.shape

                    # Draw landmarks
                    for point in hand:

                        x = int(point.x * width)
                        y = int(point.y * height)

                        cv2.circle(
                            frame,
                            (x, y),
                            5,
                            (0, 255, 0),
                            -1
                        )

                    # Draw connections
                    for start, end in HAND_CONNECTIONS:

                        p1 = hand[start]
                        p2 = hand[end]

                        x1, y1 = int(p1.x * width), int(p1.y * height)
                        x2, y2 = int(p2.x * width), int(p2.y * height)

                        cv2.line(
                            frame,
                            (x1, y1),
                            (x2, y2),
                            (255, 0, 0),
                            2
                        )

                cv2.putText(
                    frame,
                    "Hand Detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            else:

                cv2.putText(
                    frame,
                    "No Hand Detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            # Show webcam
            cv2.imshow("SignVox - Hand Detection", frame)

            # Press Q to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_hand_detection()