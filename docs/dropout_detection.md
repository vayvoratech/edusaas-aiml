Student Dropout Detection Module
Overview

The Student Dropout Detection module predicts the probability of a student dropping out of a course by analyzing learning activity, engagement, and academic performance. The model helps educators identify at-risk students early so that timely interventions can improve student retention.

Objective

Predict whether a student is at risk of dropping out using historical learning behavior.

Output:

LOW Risk
MEDIUM Risk
HIGH Risk
Technology Stack
Python
Scikit-learn
Random Forest Classifier
Pandas
NumPy
PostgreSQL
SQLAlchemy
FastAPI
Pytest
Project Structure
src/
│
├── dropout/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── predict_dropout.py
│   └── evaluate_model.py
│
├── api/
│   └── dropout_api.py
│
├── database/
│   └── database_connection.py
│
├── models/
│   ├── dropout_random_forest.pkl
│   └── dropout_feature_columns.pkl
Workflow
Student Activity Data

↓

PostgreSQL

↓

Data Cleaning

↓

Feature Engineering

↓

Random Forest Model

↓

Dropout Probability

↓

Risk Level

↓

FastAPI Response
Input Features

The model uses the following features:

Feature	Description
sessions_last_30_days	Number of learning sessions
avg_session_minutes	Average study duration
videos_watched	Videos completed
assignments_attempted	Assignments attempted
discussion_interactions	Forum participation
logins_last_30_days	Login frequency
days_since_last_login	Student inactivity
completion_percentage	Course completion
quiz_average	Average quiz score
assignment_completion_rate	Assignment completion percentage
Data Cleaning

Performed before training.

Steps:

Remove missing values
Remove duplicate records
Handle invalid values
Convert data types
Normalize required columns
Feature Engineering

Transforms raw database data into model features.

Examples:

Calculate engagement score
Calculate learning score
Calculate inactivity score
Assignment completion percentage
Quiz average
Model Selection

Algorithm Used

Random Forest Classifier

Reason:

High accuracy
Handles non-linear relationships
Robust against overfitting
Feature importance support
Fast prediction
Training Pipeline
Load Data

↓

Clean Data

↓

Feature Engineering

↓

Train/Test Split

↓

Train Random Forest

↓

Evaluate

↓

Save Model
Evaluation Metrics

Metrics used:

Accuracy
Precision
Recall
F1 Score
ROC-AUC Score
Confusion Matrix
Model Artifacts

Saved after training.

models/

dropout_random_forest.pkl

dropout_feature_columns.pkl

Purpose:

Avoid retraining every time
Faster inference
Production deployment
Prediction Flow
API Request

↓

Validate Input

↓

Load Model

↓

Feature Mapping

↓

Predict Probability

↓

Assign Risk Level

↓

Return JSON Response
API Endpoint
POST
/dropout/predict
Request
{
  "sessions_last_30_days": 15,
  "avg_session_minutes": 42,
  "videos_watched": 28,
  "assignments_attempted": 6,
  "discussion_interactions": 12,
  "logins_last_30_days": 18,
  "days_since_last_login": 3,
  "completion_percentage": 78,
  "quiz_average": 84,
  "assignment_completion_rate": 82
}
Response
{
  "dropout_prediction": 0,
  "dropout_probability": 0.18,
  "risk_level": "LOW"
}
Risk Classification
Probability	Risk
0 – 0.30	LOW
0.31 – 0.70	MEDIUM
Above 0.70	HIGH
Business Benefits
Early dropout detection
Improve student retention
Personalized interventions
Increase course completion
Better learning analytics
Reduce academic attrition
Future Enhancements
Real-time prediction
Explainable AI (SHAP)
Time-series engagement analysis
LSTM/Transformer-based prediction
Dashboard visualization
Automated intervention recommendations
Current Status
✅ Data Cleaning Completed
✅ Feature Engineering Completed
✅ Random Forest Model Trained
✅ Model Evaluation Completed
✅ Model Saved
✅ FastAPI Integration Completed
✅ PostgreSQL Integration Completed
✅ Prediction API Tested
✅ Production Folder Structure Implemented
Architecture
Client
   │
   ▼
FastAPI API
   │
   ▼
Dropout Service
   │
   ▼
Feature Engineering
   │
   ▼
Random Forest Model
   │
   ▼
Prediction
   │
   ▼
PostgreSQL
   │
   ▼
JSON Response

