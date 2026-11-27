import math
from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --------------------------------
# 1. FastAPI & CORS Setup
# --------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------
# 2. Load Trained HELLO Model
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "models" / "hello_detector.pkl"

saved_data = joblib.load(MODEL_FILE)
model = saved_data["model"]
feature_columns = saved_data["feature_columns"]
class_labels = list(model.classes_)
hello_index = class_labels.index("HELLO")

CONFIDENCE_THRESHOLD = 0.75


# --------------------------------
# 3. Landmark Normalization
# --------------------------------

class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float


class LandmarksRequest(BaseModel):
    landmarks: List[LandmarkPoint]


def normalize_landmarks(points: List[LandmarkPoint]):
    coordinates = []
    wrist = points[0]

    for pt in points:
        x = pt.x - wrist.x
        y = pt.y - wrist.y
        z = pt.z - wrist.z
        coordinates.append([x, y, z])

    scale = max(
        math.sqrt(x * x + y * y + z * z)
        for x, y, z in coordinates
    )

    if scale == 0:
        scale = 1

    normalized = []
    for x, y, z in coordinates:
        normalized.extend([
            x / scale,
            y / scale,
            z / scale,
        ])

    return normalized


# --------------------------------
# 4. API Endpoints
# --------------------------------

@app.get("/")
def home():
    return {"message": "Welcome to SignVox Backend!"}


@app.get("/test")
def test():
    return {"status": "Backend is working successfully!"}


@app.post("/predict")
def predict(payload: LandmarksRequest):
    try:
        if len(payload.landmarks) != 21:
            raise HTTPException(status_code=400, detail="Expected 21 hand landmarks")

        normalized = normalize_landmarks(payload.landmarks)

        input_data = pd.DataFrame([normalized], columns=feature_columns)
        probabilities = model.predict_proba(input_data)[0]
        hello_confidence = float(probabilities[hello_index])
        confidence_percent = round(hello_confidence * 100)

        if hello_confidence >= CONFIDENCE_THRESHOLD:
            return {
                "sign": "HELLO",
                "confidence": confidence_percent,
            }

        return {
            "sign": "",
            "confidence": confidence_percent,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))