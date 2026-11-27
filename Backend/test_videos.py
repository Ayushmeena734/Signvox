
import cv2
from pathlib import Path

dataset_path = Path("external_dataset/amrita_slr/sign project")

extensions = [".mp4", ".mov"]

for ext in extensions:
    files = list(dataset_path.rglob(f"*{ext}"))

    if not files:
        print(f"\nNo {ext} video found")
        continue

    video = files[0]
    cap = cv2.VideoCapture(str(video))

    print("\nFile:", video.name)
    print("Opened:", cap.isOpened())

    if cap.isOpened():
        print("FPS:", cap.get(cv2.CAP_PROP_FPS))
        print("Frames:", int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        print("Width:", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print("Height:", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    cap.release()
