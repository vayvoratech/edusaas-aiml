# EduSaaS Dropout Prediction Module

A production-grade machine learning system for predicting learner dropout risk using engagement, activity, and behavioral signals.

## Overview

The EduSaaS Dropout Prediction module identifies learners at risk of dropping out by analyzing:
- Engagement patterns (sessions, video consumption)
- Learning progress (completion rates, quiz performance)
- Activity trends (login frequency, recency)
- Behavioral signals (discussion participation, assignment attempts)

The system produces:
- Dropout probability (0-1)
- Binary classification (dropout/not dropout)
- Business risk level (LOW/MEDIUM/HIGH)
- Explanation factors (via engineered features)

## Architecture

```
PostgreSQL / Learner Activity
   ↓
Data Collection & Cleaning
   ↓
Feature Engineering
   ↓
Random Forest Classifier
   ↓
FastAPI Dropout Endpoint
   ↓
Probability + Classification + Risk Level
   ↓
Backend / Intervention Workflow
```

### Technology Stack

- **ML Framework**: scikit-learn (Random Forest)
- **API Layer**: FastAPI (Python)
- **Database**: PostgreSQL
- **Model Persistence**: joblib/pickle
- **Deployment**: Docker-ready

## Key Features

- **Behavioral Analytics**: 13-feature model combining engagement, learning, and activity signals
- **Risk Categorization**: LOW/MEDIUM/HIGH business risk levels
- **Real-time Prediction**: Sub-second inference for integration with intervention workflows
- **Model Explainability**: Feature importance tracking for intervention targeting
- **Prediction History**: Persistent storage for monitoring and analysis

## Model Performance

| Metric | Value |
|--------|-------|
| Accuracy | 86% |
| ROC-AUC | 0.9119 |
| Dropout Recall | 82% |
| Dataset | 1000 records × 13 features |
| Model | Random Forest |

### Why These Metrics Matter

For dropout detection, **recall is particularly critical**:
- **False Negative**: An at-risk learner is missed for intervention
- **False Positive**: Unnecessary intervention but lower operational cost
- **82% Recall** means the model identifies most positive dropout cases

## Prerequisites

- Python 3.8+
- PostgreSQL (for production persistence)
- Required Python packages (see requirements.txt)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EduSaaS
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/edusaas
MODEL_PATH=./models
PREDICTIONS_TABLE=education.dropout_predictions
```

## Model Artifacts

Ensure the following trained artifacts exist in the `models/` directory:

- `dropout_random_forest.pkl` - Trained Random Forest classifier
- `dropout_feature_columns.pkl` - Feature ordering for inference consistency

### Training the Model

```python
from src.dropout.train_model import train_dropout_model

# Load and prepare data
data = load_dropout_data()

# Train and save model
train_dropout_model(
    data_path='data/dropout_training.csv',
    model_save_path='models/dropout_random_forest.pkl',
    feature_columns_path='models/dropout_feature_columns.pkl'
)
```

## Running the Service

### Start FastAPI Service

```bash
cd src
uvicorn src.api.main:app --reload --port 8001
```

### Verify Service Health

```bash
curl http://localhost:8001/health
```

## API Endpoint

### POST /dropout/predict

**Request Format:**
```json
{
  "student_id": "21de70eb-efcd-47d0-99e3-72928628d228",
  "sessions_last_30_days": 10,
  "avg_session_minutes": 25.5,
  "videos_watched": 20,
  "assignments_attempted": 8,
  "discussion_interactions": 5,
  "logins_last_30_days": 12,
  "days_since_last_login": 2,
  "completion_percentage": 65,
  "quiz_average": 72,
  "assignment_completion_rate": 80
}
```

**Response Format:**
```json
{
  "student_id": "21de70eb-efcd-47d0-99e3-72928628d228",
  "dropout_probability": 0.31,
  "risk_level": "LOW",
  "dropout_prediction": 0,
  "prediction_time": "2026-08-24T14:30:00Z",
  "model_version": "v1.0.0"
}
```

### Risk Level Interpretation

| Risk Level | Probability Range | Action Required |
|------------|------------------|-----------------|
| **LOW** | < 0.33 | Monitor only |
| **MEDIUM** | 0.33 - 0.66 | Proactive engagement |
| **HIGH** | > 0.66 | Immediate intervention |

## Feature Engineering

The model uses 13 features derived from learner activity:

### Engagement Features
- `sessions_last_30_days` - Number of sessions in the last 30 days
- `avg_session_minutes` - Average session duration
- `logins_last_30_days` - Login frequency
- `discussion_interactions` - Community participation

### Learning Features
- `videos_watched` - Video consumption count
- `assignments_attempted` - Assignment attempts
- `quiz_average` - Average quiz performance
- `assignment_completion_rate` - Completion ratio

### Activity Features
- `days_since_last_login` - Recency of activity
- `completion_percentage` - Course completion progress

### Engineered Features
- `engagement_score` - Composite engagement indicator
- `learning_score` - Learning progress composite
- `inactivity_score` - Inactivity risk indicator

## Database Schema

### Dropout Predictions Table

```sql
CREATE TABLE education.dropout_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    dropout_probability DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    dropout_prediction BOOLEAN NOT NULL,
    prediction_time TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    model_version VARCHAR(100) DEFAULT 'v1.0.0',
    feature_snapshot JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_dropout_predictions_user_id ON education.dropout_predictions(user_id);
CREATE INDEX idx_dropout_predictions_risk_level ON education.dropout_predictions(risk_level);
CREATE INDEX idx_dropout_predictions_time ON education.dropout_predictions(prediction_time);
```

### Source Tables

| Table | Fields | Purpose |
|-------|--------|---------|
| `education.activity_logs` | sessions_last_30_days, avg_session_minutes, videos_watched, assignments_attempted, discussion_interactions, login_count, last_activity | Learner behavioral data |
| `education.login_history` | logins_last_30_days, days_since_last_login | Login frequency and inactivity signals |

## Project Structure

```
EduSaaS/
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI application
│   │   └── dropout_api.py          # Dropout prediction endpoint
│   ├── dropout/
│   │   ├── __init__.py
│   │   ├── data_cleaning.py        # Data preparation
│   │   ├── feature_engineering.py  # Feature creation
│   │   ├── predict_dropout.py      # Inference logic
│   │   └── train_model.py          # Training pipeline
│   └── database/
│       ├── database_connection.py
│       └── generate_dropout_data.py
├── models/
│   ├── dropout_random_forest.pkl
│   └── dropout_feature_columns.pkl
├── tests/
│   └── test_dropout.py
├── docs/
│   └── dropout_detection.md
├── requirements.txt
└── README.md
```

## Testing

### Unit Tests

```bash
pytest tests/test_dropout.py -v
```

### Integration Test

```bash
# Test the API endpoint
curl -X POST http://localhost:8001/dropout/predict \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-123",
    "sessions_last_30_days": 5,
    "avg_session_minutes": 15.0,
    "videos_watched": 8,
    "assignments_attempted": 3,
    "discussion_interactions": 2,
    "logins_last_30_days": 6,
    "days_since_last_login": 5,
    "completion_percentage": 40,
    "quiz_average": 65,
    "assignment_completion_rate": 70
  }'
```

## Production Considerations

### Performance Optimization

1. **Artifact Caching**: Load models once, reuse for all predictions
2. **Batch Processing**: Support batch predictions for efficient bulk operations
3. **Feature Precomputation**: Precompute engagement/learning scores in database
4. **Connection Pooling**: Use connection pooling for database operations

### Monitoring & Alerts

1. **Model Performance Tracking**:
   - Monitor prediction distribution by risk level
   - Track prediction confidence (probability)
   - Monitor feature drift over time

2. **Business Metrics**:
   - Percentage of HIGH-risk learners
   - Intervention effectiveness
   - Actual dropout rate vs. predicted rate

3. **API Metrics**:
   - Prediction latency
   - Request volume
   - Error rates

### Model Versioning

```python
# Versioning strategy
MODEL_VERSIONS = {
    'v1.0.0': 'dropout_random_forest_v1.pkl',
    'v1.1.0': 'dropout_random_forest_v1.1.pkl',
}

# Always include version in prediction responses and database storage
```

### Deployment Checklist

- [ ] Verify model artifacts exist and are accessible
- [ ] Validate feature ordering matches training
- [ ] Test API endpoint with known-good payload
- [ ] Configure database connection and persistence
- [ ] Set up monitoring for prediction distribution
- [ ] Test intervention workflow integration
- [ ] Document model version and feature schema

## Quick Start for New Engineers

1. **Read this README** to understand the dropout pipeline
2. **Review training code**: `src/dropout/train_model.py`
3. **Understand feature engineering**: `src/dropout/feature_engineering.py`
4. **Explore data cleaning**: `src/dropout/data_cleaning.py`
5. **Learn inference flow**: `src/dropout/predict_dropout.py`
6. **Check API contract**: `src/api/dropout_api.py`
7. **Verify model artifacts**: Ensure `.pkl` files exist in `models/`
8. **Start FastAPI service**: Run on port 8001
9. **Test endpoint**: Send sample prediction request
10. **Connect to backend**: Integrate with intervention workflow

## Important Implementation Notes

- **Feature Order Consistency**: Always use the persisted `dropout_feature_columns.pkl` to maintain training/inference alignment
- **Model Versioning**: Include version in predictions for traceability
- **Data Quality**: Validate feature ranges and handle missing values
- **Recall Priority**: Monitor dropout recall more closely than accuracy
- **Performance Drift**: Periodically retrain model as learner behavior patterns evolve

## Source Basis

This documentation is grounded in:
- The EduSaaS project source inventory
- AI/ML database schema specification
- Recorded dropout API test payloads
- Previously recorded model run results
