
import csv
import re
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np


# --------------------------------------------------
# 1. PROJECT PATHS AND SETTINGS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

VIDEO_DIR = (
    BASE_DIR
    / "external_dataset"
    / "amrita_slr"
    / "sign project"
)

MODEL_PATH = BASE_DIR / "hand_landmarker.task"

OUTPUT_DIR = BASE_DIR / "dataset"

OUTPUT_CSV = OUTPUT_DIR / "amrita_slr_landmarks.csv"

REPORT_CSV = OUTPUT_DIR / "amrita_slr_extraction_report.csv"

FRAMES_PER_VIDEO = 30
LANDMARK_COUNT = 21
MAX_HANDS = 1

SUPPORTED_EXTENSIONS = {".mp4", ".mov"}


# --------------------------------------------------
# 2. CSV COLUMN NAMES
# Same feature layout as collect_data.py
# --------------------------------------------------

FEATURE_COLUMNS = [
    f"{axis}{i}"
    for i in range(LANDMARK_COUNT)
    for axis in ("x", "y", "z")
]

DATA_COLUMNS = [
    "sample_id",
    "label",
    "frame",
    *FEATURE_COLUMNS,
]

REPORT_COLUMNS = [
    "video",
    "label",
    "status",
    "total_frames",
    "sampled_frames",
    "missing_frames",
    "missing_frame_indices",
    "details",
]


# --------------------------------------------------
# 3. EXTRACT LABEL FROM PARENT FOLDER
# Example: 1.bird -> bird
# --------------------------------------------------

def get_label(video_path):
    folder_name = video_path.parent.name

    label = re.sub(r"^\d+\.", "", folder_name).strip()

    return label.lower()


# --------------------------------------------------
# 4. NORMALIZE HAND LANDMARKS
# Wrist-relative normalization, consistent with
# the existing collect_data.py approach.
# --------------------------------------------------

def normalize_landmarks(hand_landmarks):

    points = np.array(
        [
            [landmark.x, landmark.y, landmark.z]
            for landmark in hand_landmarks
        ],
        dtype=np.float32,
    )

    if points.shape != (LANDMARK_COUNT, 3):
        raise ValueError(
            f"Unexpected landmark shape: {points.shape}"
        )

    # Wrist landmark (landmark 0) becomes origin.
    points = points - points[0]

    # Scale using maximum distance from wrist.
    distances = np.linalg.norm(points, axis=1)

    scale = float(np.max(distances))

    if not np.isfinite(scale) or scale < 1e-8:
        raise ValueError("Invalid landmark normalization scale")

    points = points / scale

    if not np.all(np.isfinite(points)):
        raise ValueError("Non-finite landmark values")

    return points.reshape(-1)


# --------------------------------------------------
# 5. CREATE MEDIAPIPE HAND LANDMARKER
# --------------------------------------------------

def create_landmarker():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"MediaPipe model not found: {MODEL_PATH}"
        )

    BaseOptions = mp.tasks.BaseOptions

    VisionRunningMode = mp.tasks.vision.RunningMode

    HandLandmarker = mp.tasks.vision.HandLandmarker

    HandLandmarkerOptions = (
        mp.tasks.vision.HandLandmarkerOptions
    )

    options = HandLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=str(MODEL_PATH)
        ),
       running_mode=VisionRunningMode.IMAGE,
        num_hands=MAX_HANDS,
    )

    return HandLandmarker.create_from_options(options)


# --------------------------------------------------
# 6. PROCESS ONE VIDEO
# --------------------------------------------------

def process_video(
    video_path,
    landmarker,
    sample_id,
):

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        cap.release()
        raise RuntimeError("OpenCV could not open this video")

    try:
        total_frames = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        fps = float(
            cap.get(cv2.CAP_PROP_FPS)
        )

        if total_frames < FRAMES_PER_VIDEO:
            raise ValueError(
                f"Video has only {total_frames} frames; "
                f"{FRAMES_PER_VIDEO} are required"
            )

        if not np.isfinite(fps) or fps <= 0:
            raise ValueError(f"Invalid video FPS: {fps}")

        # Select 30 evenly spaced, unique frame indices.
        frame_indices = np.linspace(
            0,
            total_frames - 1,
            num=FRAMES_PER_VIDEO,
            dtype=np.int64,
        )

        label = get_label(video_path)

        extracted_rows = []
        missing_indices = []

       

        for frame_number, frame_index in enumerate(frame_indices):

            # Seek to the selected video frame.
            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(frame_index),
            )

            success, frame = cap.read()

            if not success or frame is None:
                missing_indices.append(frame_number)
                continue

            # OpenCV BGR -> MediaPipe RGB.
            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame,
            )

            result = landmarker.detect(mp_image)

            # No hand detected in this sampled frame.
            if not result.hand_landmarks:
                missing_indices.append(frame_number)
                continue

            # Only the first detected hand is used.
            hand = result.hand_landmarks[0]

            normalized = normalize_landmarks(hand)

            row = {
                "sample_id": sample_id,
                "label": label,
                "frame": frame_number,
            }

            for column, value in zip(
                FEATURE_COLUMNS,
                normalized,
            ):
                row[column] = float(value)

            extracted_rows.append(row)

        # Do not save incomplete video sequences.
        if missing_indices:
            return {
                "success": False,
                "label": label,
                "total_frames": total_frames,
                "sampled_frames": FRAMES_PER_VIDEO,
                "missing_frames": len(missing_indices),
                "missing_frame_indices": missing_indices,
                "rows": [],
                "details": "Hand missing or frame unreadable",
            }

        return {
            "success": True,
            "label": label,
            "total_frames": total_frames,
            "sampled_frames": FRAMES_PER_VIDEO,
            "missing_frames": 0,
            "missing_frame_indices": [],
            "rows": extracted_rows,
            "details": "Successfully extracted",
        }

    finally:
        cap.release()


# --------------------------------------------------
# 7. MAIN EXTRACTION PROCESS
# --------------------------------------------------

def main():

    print("=" * 55)
    print("SIGNVOX - AMRITA SLR LANDMARK EXTRACTION")
    print("=" * 55)

    if not VIDEO_DIR.exists():
        print("ERROR: Dataset folder not found:")
        print(VIDEO_DIR)
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    video_files = sorted(
        [
            path
            for path in VIDEO_DIR.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ],
        key=lambda path: str(path).lower(),
    )

    if not video_files:
        print("No MP4 or MOV videos found.")
        return

    print(f"Videos found: {len(video_files)}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Report CSV: {REPORT_CSV}")

    successful = 0
    skipped = 0
    failed = 0

    # One landmarker instance is reused for all videos.
    with create_landmarker() as landmarker:

        with (
            open(
                OUTPUT_CSV,
                "w",
                newline="",
                encoding="utf-8",
            ) as data_file,
            open(
                REPORT_CSV,
                "w",
                newline="",
                encoding="utf-8",
            ) as report_file,
        ):

            data_writer = csv.DictWriter(
                data_file,
                fieldnames=DATA_COLUMNS,
            )

            report_writer = csv.DictWriter(
                report_file,
                fieldnames=REPORT_COLUMNS,
            )

            data_writer.writeheader()
            report_writer.writeheader()

            for video_number, video_path in enumerate(
                video_files,
                start=1,
            ):

                relative_path = video_path.relative_to(
                    VIDEO_DIR
                )

                sample_id = f"amrita_{video_number:04d}"

                print(
                    f"\n[{video_number}/{len(video_files)}] "
                    f"{relative_path}"
                )

                try:
                    result = process_video(
                        video_path,
                        landmarker,
                        sample_id,
                    )

                    if result["success"]:

                        data_writer.writerows(
                            result["rows"]
                        )

                        successful += 1
                        status = "SUCCESS"

                        print(
                            f"  SUCCESS: "
                            f"{FRAMES_PER_VIDEO} frames extracted"
                        )

                    else:
                        skipped += 1
                        status = "SKIPPED"

                        print(
                            f"  SKIPPED: "
                            f"{result['missing_frames']} "
                            f"missing frames"
                        )

                    report_writer.writerow({
                        "video": str(relative_path),
                        "label": result["label"],
                        "status": status,
                        "total_frames": result["total_frames"],
                        "sampled_frames": result["sampled_frames"],
                        "missing_frames": result["missing_frames"],
                        "missing_frame_indices": ";".join(
                            map(
                                str,
                                result["missing_frame_indices"],
                            )
                        ),
                        "details": result["details"],
                    })

                except Exception as error:

                    failed += 1

                    print(f"  ERROR: {error}")

                    report_writer.writerow({
                        "video": str(relative_path),
                        "label": get_label(video_path),
                        "status": "ERROR",
                        "total_frames": "",
                        "sampled_frames": FRAMES_PER_VIDEO,
                        "missing_frames": "",
                        "missing_frame_indices": "",
                        "details": str(error),
                    })

    # --------------------------------------------------
    # 8. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 55)
    print("EXTRACTION COMPLETED")
    print("=" * 55)

    print("Total videos:", len(video_files))
    print("Successful:", successful)
    print("Skipped:", skipped)
    print("Failed:", failed)

    print(
        "Successful video sequences:",
        successful,
    )

    print(
        "Total landmark rows:",
        successful * FRAMES_PER_VIDEO,
    )

    print("\nDataset saved at:")
    print(OUTPUT_CSV)

    print("\nExtraction report saved at:")
    print(REPORT_CSV)


# --------------------------------------------------
# 9. RUN SCRIPT
# --------------------------------------------------

if __name__ == "__main__":
    main()
