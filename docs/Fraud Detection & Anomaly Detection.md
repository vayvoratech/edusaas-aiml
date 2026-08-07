# Fraud Detection System Documentation

### EduSaaS AI Platform

**Module:** Fraud Detection
**Version:** 1.0
**Model Type:** Random Forest + Isolation Forest
**Framework:** Scikit-learn
**Database:** PostgreSQL
**API Framework:** FastAPI

---

# 1. Objective

The Fraud Detection module identifies suspicious student enrollments and abnormal platform activities by analyzing learning behavior, login patterns, device usage, and enrollment information.

The module combines:

* **Random Forest** for supervised fraud classification.
* **Isolation Forest** for unsupervised anomaly detection.

This dual-model architecture enables the system to detect both known fraud patterns and previously unseen suspicious behaviors.

---

# 2. Business Problem

Online learning platforms are vulnerable to fraudulent activities such as:

* Fake student registrations
* Multiple account creation
* Credential sharing
* Automated (bot) enrollments
* Suspicious login activities
* Multiple device usage
* Frequent IP switching
* Artificial course completion

These activities impact:

* Learning analytics
* Recommendation systems
* Student performance reports
* Certification integrity
* Business insights

The Fraud Detection module continuously evaluates student activity and assigns a fraud risk level.

---

# 3. Technology Stack

| Component            | Technology       |
| -------------------- | ---------------- |
| Programming Language | Python           |
| Machine Learning     | Scikit-learn     |
| Classification Model | Random Forest    |
| Anomaly Detection    | Isolation Forest |
| Database             | PostgreSQL       |
| API                  | FastAPI          |
| Model Serialization  | Joblib           |
| Testing              | Pytest           |

---

# 4. Project Structure

```
src/
│
├── fraud/
│   ├── preprocessing.py
│   ├── fraud_feature_calculator.py
│   ├── feature_engineering.py
│   ├── fraud_dataset.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── model_loader.py
│   ├── fraud_repository.py
│   ├── fraud_service.py
│   ├── predict_fraud.py
│   └── __init__.py
│
├── api/
│   └── fraud.py
│
models/
│
└── fraud/
    ├── fraud_random_forest.pkl
    ├── fraud_isolation_forest.pkl
    └── fraud_feature_columns.pkl
```

---

# 5. Database Tables Used

## enrollments

Stores enrollment information including:

* Student ID
* Course ID
* Completion Percentage
* Watch Time
* Quiz Score
* Rating
* Payment Status
* Enrollment Source
* Enrollment Status

---

## activity_logs

Stores platform activity including:

* Sessions
* Videos Watched
* Assignments Attempted
* Discussion Interactions
* Login Count
* Device Count
* IP Changes

---

## fraud_predictions

Stores prediction history.

Columns include:

* Prediction ID
* Student ID
* Fraud Probability
* Risk Level
* Fraud Prediction
* Anomaly Prediction
* Prediction Timestamp

---

# 6. Data Preprocessing

The preprocessing stage performs:

* Data loading from PostgreSQL
* Duplicate removal
* Missing value handling
* Data validation
* Feature selection

Output:

Clean dataset for feature engineering.

---

# 7. Feature Engineering

A centralized feature calculator generates engineered features.

### Engagement Score

Measures student engagement based on:

* Videos watched
* Assignments attempted
* Discussion interactions
* Course completion

---

### Login Frequency Score

Measures login consistency.

Formula:

```
Login Count / Sessions
```

---

### Device Risk Score

Measures device-related risk.

Formula:

```
Device Count + IP Changes
```

---

### Learning Consistency Score

Measures learning performance.

Formula:

```
(Completion Percentage + Quiz Score) / 2
```

---

### Suspicious Activity Score

Measures suspicious platform behavior using:

* Login Count
* Device Count
* IP Changes
* Payment Status
* Enrollment Source
* Enrollment Status

---

### Fraud Risk Score

Combines multiple fraud indicators into a single risk metric.

---

# 8. Machine Learning Models

## Random Forest

Purpose:

Predict whether a student is fraudulent using historical labeled data.

Output:

* Fraud Probability
* Fraud Prediction

---

## Isolation Forest

Purpose:

Identify abnormal behavior without requiring labeled data.

Output:

* Normal
* Anomaly

---

# 9. Model Training Pipeline

```
PostgreSQL
        │
        ▼
Preprocessing
        │
        ▼
Feature Engineering
        │
        ▼
Fraud Dataset
        │
        ▼
Train-Test Split
        │
        ▼
Random Forest Training
        │
        ▼
Isolation Forest Training
        │
        ▼
Model Evaluation
        │
        ▼
Save Models
```

---

# 10. Model Evaluation

Evaluation Metrics:

* Accuracy
* Precision
* Recall
* F1 Score
* ROC-AUC Score
* Confusion Matrix
* Classification Report
* Feature Importance

These metrics help evaluate model performance and identify areas for improvement.

---

# 11. Prediction Workflow

```
API Request
      │
      ▼
Fraud Service
      │
      ▼
Feature Calculator
      │
      ▼
Random Forest
      │
      ▼
Isolation Forest
      │
      ▼
Risk Level Calculation
      │
      ▼
Save Prediction
      │
      ▼
API Response
```

---

# 12. Risk Levels

| Fraud Probability | Risk Level |
| ----------------- | ---------- |
| < 0.50            | LOW        |
| 0.50 – 0.79       | MEDIUM     |
| ≥ 0.80            | HIGH       |

---

# 13. API Endpoint

### Endpoint

```
POST /fraud/predict
```

### Sample Request

```json
{
  "student_id": 101,
  "completion_percentage": 82,
  "watch_time_minutes": 2100,
  "quiz_score": 86,
  "rating": 5,
  "sessions_last_30_days": 25,
  "avg_session_minutes": 42,
  "videos_watched": 65,
  "assignments_attempted": 12,
  "discussion_interactions": 18,
  "login_count": 32,
  "device_count": 1,
  "ip_changes": 0,
  "payment_status": "PAID",
  "enrollment_source": "WEB",
  "enrollment_status": "ACTIVE"
}
```

### Sample Response

```json
{
  "student_id": 101,
  "fraud_probability": 0.38,
  "risk_level": "LOW",
  "fraud_prediction": "NORMAL",
  "anomaly_status": "ANOMALY"
}
```

---

# 14. Repository Layer

Responsibilities:

* Store prediction results
* Manage database transactions
* Handle rollbacks
* Log failures and successes

---

# 15. Service Layer

Responsibilities:

* Receive prediction requests
* Generate engineered features
* Load trained models
* Execute fraud prediction
* Execute anomaly detection
* Calculate risk level
* Save prediction results
* Return API response

---

# 16. Logging

The module logs:

* Prediction requests
* Model loading
* Database operations
* Successful predictions
* Exceptions
* Prediction failures

This improves traceability and simplifies production debugging.

---

# 17. Testing

Testing is performed using **Pytest** and **FastAPI TestClient**.

Test coverage includes:

* API availability
* Request validation
* Response validation
* Prediction pipeline
* HTTP status verification

---

# 18. Current Limitations

* Fraud labels are currently generated from synthetic data.
* Model performance depends on the quality of generated fraud scenarios.
* Real production data will improve precision, recall, and ROC-AUC.

---

# 19. Future Enhancements

* Train using real EduSaaS platform data.
* Add browser fingerprinting and device fingerprinting.
* Integrate geolocation-based risk analysis.
* Add session behavior analytics.
* Implement real-time fraud alerts.
* Create fraud monitoring dashboards.
* Add model retraining pipeline.
* Monitor model drift and data drift.
* Introduce explainable AI (e.g., SHAP) for prediction transparency.

---

# 20. Conclusion

The Fraud Detection module provides a scalable and modular AI solution for identifying suspicious enrollments and abnormal student behavior within the EduSaaS platform. By combining supervised classification (Random Forest) with unsupervised anomaly detection (Isolation Forest), the system supports proactive fraud monitoring, enhances platform security, and establishes a foundation for future improvements as real-world data becomes available.
