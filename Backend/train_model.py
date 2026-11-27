
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


# --------------------------------
# 1. Paths
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "dataset" / "signvox_dataset.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

MODEL_FILE = MODEL_DIR / "hello_detector.pkl"


# --------------------------------
# 2. Load Dataset
# --------------------------------

print("Loading dataset...")

df = pd.read_csv(CSV_FILE)

print("Dataset shape:", df.shape)
print("Labels:", df["label"].value_counts().to_dict())


# --------------------------------
# 3. Prepare Features
# --------------------------------

feature_columns = [
    column for column in df.columns
    if column.startswith(("x", "y", "z"))
]

X = df[feature_columns].astype(float)
y = df["label"].astype(str)

groups = df["sample_id"]


# --------------------------------
# 4. Split by Recording
# --------------------------------

splitter = GroupShuffleSplit(
    n_splits=100,
    test_size=0.25,
    random_state=42
)

train_indices = None
test_indices = None

for candidate_train, candidate_test in splitter.split(X, y, groups):

    train_labels = set(y.iloc[candidate_train])
    test_labels = set(y.iloc[candidate_test])

    if (
        train_labels == {"HELLO", "NOT_HELLO"}
        and test_labels == {"HELLO", "NOT_HELLO"}
    ):
        train_indices = candidate_train
        test_indices = candidate_test
        break

if train_indices is None:
    raise ValueError("Could not create a split containing both labels.")

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]


# --------------------------------
# 5. Train Random Forest
# --------------------------------

print("\nTraining model...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)


# --------------------------------
# 6. Evaluate Model
# --------------------------------

predictions = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, predictions))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        labels=["HELLO", "NOT_HELLO"],
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        predictions,
        labels=["HELLO", "NOT_HELLO"]
    )
)


# --------------------------------
# 7. Save Model
# --------------------------------

joblib.dump(
    {
        "model": model,
        "feature_columns": feature_columns,
        "labels": ["HELLO", "NOT_HELLO"]
    },
    MODEL_FILE
)

print("\nModel saved successfully!")
print("Model path:", MODEL_FILE)
