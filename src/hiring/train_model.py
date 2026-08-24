import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import train_test_split

from src.hiring.hiring_dataset import HiringDataset


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = (
    "data/hiring/"
    "hiring_training_dataset.csv"
)

MODEL_DIR = "models/hiring"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "hiring_random_forest.pkl"
)

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "hiring_feature_columns.pkl"
)


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# LOAD DATASET
# ============================================================

print(
    "\n=========================================="
)

print(
    "EduSaaS Predictive Hiring Model Training"
)

print(
    "==========================================\n"
)

dataframe = pd.read_csv(
    DATA_PATH
)

print(
    f"Dataset Shape : {dataframe.shape}"
)


# ============================================================
# PREPARE DATASET
# ============================================================

dataset = HiringDataset(
    dataframe
)

X, y = dataset.prepare()

print(
    f"Features : {X.shape}"
)

print(
    f"Labels   : {y.shape}"
)

print(
    "\nTarget Distribution:"
)

print(
    y.value_counts()
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)

print(
    f"\nTraining Records : {len(X_train)}"
)

print(
    f"Testing Records  : {len(X_test)}"
)


# ============================================================
# RANDOM FOREST
# ============================================================

print(
    "\nTraining Random Forest...\n"
)

model = RandomForestClassifier(

    n_estimators=300,

    max_depth=12,

    min_samples_split=5,

    min_samples_leaf=2,

    class_weight="balanced",

    random_state=42,

    n_jobs=-1

)

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(
    X_test
)

probabilities = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

confusion = confusion_matrix(
    y_test,
    predictions
)


print(
    "\n=========================================="
)

print(
    "Predictive Hiring Model Evaluation"
)

print(
    "==========================================\n"
)

print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)

print(
    f"ROC AUC   : {roc_auc:.4f}"
)

print(
    "\nConfusion Matrix:"
)

print(
    confusion
)

print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print(
    "\nFeature Importance:"
)

feature_importance = sorted(

    zip(
        X.columns,
        model.feature_importances_
    ),

    key=lambda item: item[1],

    reverse=True
)

for feature, importance in feature_importance:

    print(
        f"{feature:<35}"
        f"{importance:.4f}"
    )


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    list(X.columns),
    FEATURE_PATH
)


print(
    "\n=========================================="
)

print(
    "Model Saved Successfully"
)

print(
    "=========================================="
)

print(
    f"\nModel   : {MODEL_PATH}"
)

print(
    f"Features: {FEATURE_PATH}"
)