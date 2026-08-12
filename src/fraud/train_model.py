import os
import joblib

from sklearn.ensemble import (
    RandomForestClassifier,
    IsolationForest
)

from sklearn.model_selection import train_test_split

from src.fraud.preprocessing import FraudPreprocessor
from src.fraud.feature_engineering import FraudFeatureEngineering
from src.fraud.fraud_dataset import FraudDataset
from src.fraud.evaluate_model import evaluate_model


# ----------------------------------------
# Configuration
# ----------------------------------------

MODEL_DIR = "models/fraud"

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ----------------------------------------
# Load Dataset
# ----------------------------------------

print("\nLoading Fraud Dataset...\n")

processor = FraudPreprocessor()

dataframe = processor.preprocess()

engineer = FraudFeatureEngineering(
    dataframe
)

dataframe = engineer.create_features()

dataset = FraudDataset(
    dataframe
)

X, y = dataset.prepare()

print("\nFeature Columns Used\n")

for column in X.columns:

    print(column)

print(f"Dataset Shape : {X.shape}")


# ----------------------------------------
# Train Test Split
# ----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,

    stratify=y

)

print(f"Training Records : {len(X_train)}")

print(f"Testing Records : {len(X_test)}")


# ----------------------------------------
# Train Random Forest
# ----------------------------------------

print("\nTraining Random Forest...\n")

rf_model = RandomForestClassifier(

    n_estimators=200,

    max_depth=12,

    class_weight="balanced",

    random_state=42

)

rf_model.fit(

    X_train,

    y_train

)


# ----------------------------------------
# Train Isolation Forest
# ----------------------------------------

print("\nTraining Isolation Forest...\n")

iso_model = IsolationForest(

    contamination=0.08,

    random_state=42

)

iso_model.fit(X_train)


# ----------------------------------------
# Evaluate Random Forest
# ----------------------------------------

print("\nEvaluating Fraud Detection Model...\n")

metrics = evaluate_model(

    rf_model,

    X_test,

    y_test

)


# ----------------------------------------
# Feature Importance
# ----------------------------------------

feature_importance = sorted(

    zip(

        X.columns,

        rf_model.feature_importances_

    ),

    key=lambda x: x[1],

    reverse=True

)

print("\nTop Feature Importance\n")

for feature, importance in feature_importance:

    print(

        f"{feature:<35}{importance:.4f}"

    )



# ----------------------------------------
# Save Models
# ----------------------------------------

print("\nSaving Models...\n")

joblib.dump(

    rf_model,

    os.path.join(

        MODEL_DIR,

        "fraud_random_forest.pkl"

    )

)

joblib.dump(

    iso_model,

    os.path.join(

        MODEL_DIR,

        "fraud_isolation_forest.pkl"

    )

)

joblib.dump(

    list(X.columns),

    os.path.join(

        MODEL_DIR,

        "fraud_feature_columns.pkl"

    )

)

print("\nModels Saved Successfully")

print(f"Location : {MODEL_DIR}")

print("\nFeature Columns Saved Successfully")