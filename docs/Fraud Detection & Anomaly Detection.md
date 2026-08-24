# EduSaaS Fraud & Anomaly Detection Module

A production-grade dual-detection system combining supervised fraud classification with unsupervised anomaly detection for identifying suspicious learner behavior.

## Overview

The Fraud & Anomaly Detection module protects the educational platform by:
- **Supervised Detection**: Random Forest classifier identifies patterns matching known fraudulent behavior
- **Unsupervised Detection**: Isolation Forest flags unusual behavioral patterns
- **Risk Assessment**: Business risk levels (LOW/MEDIUM/HIGH) for intervention prioritization
- **Independent Signals**: Fraud classification and anomaly detection operate separately for comprehensive coverage

## Architecture

```
Enrollment + Activity Data
   ↓
FraudPreprocessor
   ↓
FraudFeatureEngineering
   ↓
┌─────────────────────────────┐
│ Random Forest → Fraud Prediction + Probability │
│ Isolation Forest → Anomaly Detection            │
└─────────────────────────────┘
   ↓
FraudService
   ↓
Risk Classification
   ↓
Prediction Repository
   ↓
API Response / Backend
```

### Technology Stack

- **Supervised Model**: Random Forest Classifier (scikit-learn)
- **Unsupervised Model**: Isolation Forest (scikit-learn)
- **API Layer**: FastAPI
- **Database**: PostgreSQL
- **Model Persistence**: joblib

## Key Features

- **Dual Detection Strategy**: Supervised fraud classification + unsupervised anomaly detection
- **Independent Signals**: Fraud prediction and anomaly status can differ
- **Business Risk Levels**: LOW/MEDIUM/HIGH for operational decision-making
- **Feature Engineering**: Comprehensive behavioral and enrollment features
- **Model Explainability**: Feature importance for fraud classification
- **Prediction Persistence**: Full audit trail with model versioning

## Detection Strategy

| Component | Type | Purpose |
|-----------|------|---------|
| **Random Forest** | Supervised Classification | Predicts fraudulent behavior with probability |
| **Isolation Forest** | Unsupervised Anomaly Detection | Identifies unusual behavior patterns |
| **Risk Layer** | Business Rules | Maps probability to LOW/MEDIUM/HIGH |

## Model Configuration

| Model | Configuration | Purpose |
|-------|--------------|---------|
| **Random Forest** | n_estimators=200, max_depth=12, class_weight='balanced', random_state=42 | Fraud classification |
| **Isolation Forest** | contamination=0.08, random_state=42 | Anomaly detection |

## Source Data Features

The model uses comprehensive learner and enrollment data:

### Enrollment Features
- `student_id` - Learner identifier
- `course_id` - Course identifier
- `enrollment_source` - How learner enrolled
- `enrollment_status` - Current enrollment state
- `payment_status` - Payment state

### Behavioral Features
- `completion_percentage` - Course completion progress
- `watch_time_minutes` - Video consumption time
- `quiz_score` - Assessment performance
- `sessions_last_30_days` - Recent activity level
- `avg_session_minutes` - Engagement depth
- `videos_watched` - Content consumption
- `assignments_attempted` - Assignment participation
- `discussion_interactions` - Community engagement
- `login_count` - Platform activity

### Fraud Indicators
- `device_count` - Number of devices used
- `ip_changes` - IP address changes
- `suspicious_activity_score` - Composite fraud indicator
- `rating` - Course rating (if applicable)
- `is_fraud` - Training label

## Prerequisites

- Python 3.8+
- PostgreSQL
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
MODEL_PATH=./models/fraud
PREDICTIONS_TABLE=education.fraud_predictions
API_PORT=8002
```

## Model Artifacts

Ensure the following artifacts exist in `models/fraud/`:

- `fraud_random_forest.pkl` - Trained Random Forest classifier
- `fraud_isolation_forest.pkl` - Trained Isolation Forest detector
- `fraud_feature_columns.pkl` - Feature ordering for inference consistency

### Training the Models

```python
from src.fraud.train_model import train_fraud_models

# Train both models
train_fraud_models(
    data_path='data/fraud_training.csv',
    model_dir='models/fraud/',
    random_forest_params={
        'n_estimators': 200,
        'max_depth': 12,
        'class_weight': 'balanced',
        'random_state': 42
    },
    isolation_forest_params={
        'contamination': 0.08,
        'random_state': 42
    }
)
```

## Running the Service

### Start FastAPI Service

```bash
cd src
uvicorn src.api.main:app --reload --port 8002
```

### Verify Service Health

```bash
curl http://localhost:8002/health
```

## API Endpoint

### POST /fraud/predict

**Request Format:**
```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "course_id": "CS101",
  "completion_percentage": 45,
  "watch_time_minutes": 320,
  "quiz_score": 78,
  "rating": 4.5,
  "payment_status": "completed",
  "enrollment_source": "direct",
  "enrollment_status": "active",
  "sessions_last_30_days": 15,
  "avg_session_minutes": 28.5,
  "videos_watched": 24,
  "assignments_attempted": 6,
  "discussion_interactions": 8,
  "login_count": 20,
  "device_count": 2,
  "ip_changes": 1,
  "suspicious_activity_score": 0.15
}
```

**Response Format:**
```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "fraud_probability": 0.385,
  "risk_level": "LOW",
  "fraud_prediction": "NORMAL",
  "anomaly_status": "ANOMALY",
  "prediction_time": "2026-08-24T14:30:00Z",
  "model_version": "v1.0.0"
}
```

### Risk Level Interpretation

| Fraud Probability | Risk Level | Action |
|-------------------|------------|--------|
| ≥ 0.80 | **HIGH** | Immediate investigation required |
| 0.50 - 0.79 | **MEDIUM** | Enhanced monitoring |
| < 0.50 | **LOW** | Regular monitoring |

### Output Interpretation

The system provides two independent signals:

| Signal | Values | Meaning |
|--------|--------|---------|
| **fraud_prediction** | FRAUD / NORMAL | Matches known fraud patterns |
| **anomaly_status** | ANOMALY / NORMAL | Unusual behavior relative to distribution |

**Key Insight**: A learner can be classified as NORMAL by the fraud classifier but ANOMALY by Isolation Forest, indicating the behavior is unusual but doesn't match known fraud patterns.

## Database Schema

### Fraud Predictions Table

```sql
CREATE TABLE education.fraud_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    fraud_probability DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    fraud_prediction BOOLEAN NOT NULL,
    anomaly_prediction BOOLEAN NOT NULL,
    prediction_time TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    model_version VARCHAR(100) DEFAULT 'v1.0.0',
    feature_snapshot JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fraud_predictions_user_id ON education.fraud_predictions(user_id);
CREATE INDEX idx_fraud_predictions_risk_level ON education.fraud_predictions(risk_level);
CREATE INDEX idx_fraud_predictions_anomaly ON education.fraud_predictions(anomaly_prediction);
```

### Source Tables

| Table | Fields | Purpose |
|-------|--------|---------|
| `education.activity_logs` | device_count, ip_changes, suspicious_activity_score, login_count | Behavioral fraud indicators |
| `enrollment_data` | enrollment_source, enrollment_status, payment_status | Enrollment patterns |

## Project Structure

```
EduSaaS/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   └── fraud.py             # Fraud detection endpoints
│   ├── fraud/
│   │   ├── __init__.py
│   │   ├── preprocessing.py     # Data cleaning
│   │   ├── feature_engineering.py # Training features
│   │   ├── fraud_dataset.py     # X/y separation
│   │   ├── train_model.py       # Model training
│   │   ├── evaluate_model.py    # Model evaluation
│   │   ├── fraud_feature_calculator.py # Inference features
│   │   ├── fraud_model_loader.py # Model loading
│   │   ├── fraud_service.py     # End-to-end inference
│   │   ├── predict_fraud.py     # Public prediction function
│   │   └── fraud_repository.py  # Database persistence
│   └── database/
│       └── database_connection.py
├── models/
│   └── fraud/
│       ├── fraud_random_forest.pkl
│       ├── fraud_isolation_forest.pkl
│       └── fraud_feature_columns.pkl
├── tests/
│   └── test_fraud.py
├── requirements.txt
└── README.md
```

## Testing

### Unit Tests

```bash
pytest tests/test_fraud.py -v
```

### Integration Test

```bash
# Test fraud detection endpoint
curl -X POST http://localhost:8002/fraud/predict \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-123",
    "course_id": "CS101",
    "completion_percentage": 45,
    "watch_time_minutes": 320,
    "quiz_score": 78,
    "rating": 4.5,
    "payment_status": "completed",
    "enrollment_source": "direct",
    "enrollment_status": "active",
    "sessions_last_30_days": 15,
    "avg_session_minutes": 28.5,
    "videos_watched": 24,
    "assignments_attempted": 6,
    "discussion_interactions": 8,
    "login_count": 20,
    "device_count": 2,
    "ip_changes": 1,
    "suspicious_activity_score": 0.15
  }'
```

## Production Considerations

### Performance Optimization

1. **Model Caching**: Load models once, reuse for all predictions
2. **Batch Processing**: Support batch predictions for efficiency
3. **Feature Precomputation**: Precompute suspicious_activity_score in database
4. **Connection Pooling**: Use connection pooling for database operations

### Monitoring & Alerts

1. **Model Performance**:
   - Monitor fraud recall and precision
   - Track false positive rate
   - Monitor anomaly detection rate (should be ~8%)

2. **Business Metrics**:
   - Percentage of HIGH-risk learners
   - Distribution of risk levels
   - Correlation between fraud and anomaly signals

3. **API Metrics**:
   - Prediction latency
   - Request volume
   - Error rates

### Security Considerations

1. **Data Protection**: Fraud predictions are security-sensitive
2. **Access Control**: Restrict API access to authorized services
3. **Audit Trail**: Persist all predictions for regulatory compliance
4. **Feature Validation**: Validate all input features before prediction

### Model Versioning

```python
# Versioning strategy
MODEL_VERSIONS = {
    'v1.0.0': {
        'random_forest': 'fraud_random_forest_v1.pkl',
        'isolation_forest': 'fraud_isolation_forest_v1.pkl',
        'feature_columns': 'fraud_feature_columns_v1.pkl'
    }
}

# Always include version in predictions
```

### Deployment Checklist

- [ ] Verify all three model artifacts exist
- [ ] Validate feature ordering matches training
- [ ] Test API with known-good payload
- [ ] Configure database connection and persistence
- [ ] Set up monitoring for fraud/anomaly rates
- [ ] Implement alerting for HIGH-risk predictions
- [ ] Document model version and feature schema
- [ ] Review security controls for prediction data

## Important Implementation Notes

- **Feature Consistency**: Always use persisted `fraud_feature_columns.pkl` for inference
- **Model Versioning**: Track both models and feature schema together
- **Independent Signals**: Fraud and anomaly outputs serve different purposes
- **Contamination Setting**: Isolation Forest expects ~8% anomalies (current configuration)
- **Class Imbalance**: Random Forest uses class_weight='balanced' for imbalanced data

## Quick Start for New Engineers

1. **Read this README** to understand the dual-detection strategy
2. **Review preprocessing**: `src/fraud/preprocessing.py`
3. **Understand feature engineering**: `src/fraud/feature_engineering.py`
4. **Explore training pipeline**: `src/fraud/train_model.py`
5. **Check inference flow**: `src/fraud/fraud_service.py`
6. **Review model loading**: `src/fraud/fraud_model_loader.py`
7. **Test API endpoint**: Send sample request
8. **Verify persistence**: Check `education.fraud_predictions` table
9. **Monitor performance**: Track risk distribution and anomaly rate

## Source Basis

This documentation is grounded in:
- The EduSaaS fraud source material
- AI/ML database specifications
- Confirmed Random Forest + Isolation Forest implementation
- Documented model hyperparameters and risk thresholds

---

*This documentation reflects the current implementation and should be updated with each model version release.*