# EduSaaS — Sentiment Analysis System



### 1. Module Overview

**Module:** Discussion Sentiment Analysis
**Model:** DistilBERT
**Purpose:** Analyze learner discussion/forum text and classify the sentiment as:

```text
NEGATIVE
NEUTRAL
POSITIVE
```

The system also returns probability scores for each sentiment and the model confidence.

The finalized backend schema stores the prediction in:

```text
education.sentiment_predictions
```

with fields including `post_id`, `prediction`, `confidence`, the three sentiment scores, prediction timestamp, and model version. 

---

# 2. Production Architecture

```text id="p7g1jv"
                    Frontend / Client
                           │
                           ▼
                    Node.js Backend
                         :3000
                           │
                           ▼
                Sentiment Controller
                           │
                           ▼
             Sentiment Python Service
                           │
                           │ HTTP/JSON
                           ▼
                 Python FastAPI
                         :8002
                           │
                           ▼
                      DistilBERT
                           │
                           ▼
                  Sentiment Prediction
                           │
                           ▼
                       Node.js
                           │
                           ▼
                PostgreSQL
                           │
                           ▼
        education.sentiment_predictions
```

### Architecture principle

```text
Node.js
   = Database + application layer

Python
   = ML inference layer
```

Python does **not** directly connect to PostgreSQL during runtime.

---

# 3. Model

### Model

**DistilBERT**

DistilBERT is a compressed Transformer-based language model used here for text classification.

The model receives the discussion post text and produces logits for three classes:

```text id="s4u3ad"
0 → NEGATIVE
1 → NEUTRAL
2 → POSITIVE
```

The application maps the model output to these human-readable labels.

---

# 4. Input Contract

The production API accepts:

```json id="o8x9i1"
{
  "post_id": "UUID",
  "post_text": "This course is absolutely amazing and very useful."
}
```

### `post_id`

```text
Type: UUID
Purpose: Identifies the original discussion/community post
```

### `post_text`

```text
Type: string
Minimum length: 2
Maximum length: 5000
```

The production contract uses `post_id` rather than the legacy `student_id`, `course_id`, and `discussion_id` combination.

---

# 5. Text Processing Pipeline

The incoming text is passed to the model tokenizer.

```python id="o0b9uw"
encoding = tokenizer(
    post_text,
    return_tensors="pt",
    truncation=True,
    padding=True
)
```

The processing flow is:

```text id="yzj9h3"
Raw discussion text
        ↓
DistilBERT tokenizer
        ↓
Token IDs
        ↓
Attention mask
        ↓
DistilBERT
        ↓
Logits
        ↓
Softmax
        ↓
Class probabilities
```

`truncation=True` prevents oversized text from exceeding the model's input constraints.

---

# 6. Model Inference

The model performs inference using:

```python id="j3r9dk"
with torch.no_grad():
    outputs = model(
        **encoding
    )
```

`torch.no_grad()` prevents gradient calculation during inference, reducing unnecessary memory and computation.

The model returns:

```text id="xj6r0k"
outputs.logits
```

These logits are converted into probabilities.

---

# 7. Probability Calculation

The system applies Softmax:

```python id="1x3x2w"
probabilities = torch.softmax(
    outputs.logits,
    dim=1
)
```

This produces a probability distribution across the three sentiment classes.

Example:

```text id="p8s5m0"
NEGATIVE → 1.74%
NEUTRAL  → 1.23%
POSITIVE → 97.03%
```

The probabilities sum approximately to:

```text
100%
```

---

# 8. Sentiment Prediction

The highest probability class becomes the final sentiment.

Example:

```text id="z9d6ko"
NEGATIVE = 1.74%
NEUTRAL  = 1.23%
POSITIVE = 97.03%

                ↓

Prediction = POSITIVE
```

The maximum probability is also used as the confidence value.

---

# 9. Model Confidence

The system extracts:

```python id="kq5n2z"
confidence, prediction = torch.max(
    probabilities,
    dim=1
)
```

Example:

```text id="04p7nz"
confidence = 97.03%
```

This means the model's highest predicted class has a probability of 97.03%.

---

# 10. Output Contract

Python returns:

```json id="8d0c0k"
{
  "post_id": "21de70eb-efcd-47d0-99e3-72928628d228",
  "prediction": "POSITIVE",
  "confidence": 97.03,
  "negative_score": 1.74,
  "neutral_score": 1.23,
  "positive_score": 97.03,
  "model_version": "1.0.0"
}
```

This response maps directly to the database persistence fields.

---

# 11. API Architecture

### Python API

```text id="0t7k0z"
POST /sentiment/predict-sentiment
```

Python service:

```text
http://127.0.0.1:8002
```

### Health endpoint

```text id="j0p9a1"
GET /sentiment/health
```

### Node API

The application-facing endpoint is:

```text id="9u5p3m"
POST /api/sentiment/predict
```

The frontend should communicate with Node rather than directly calling the Python service.

---

# 12. Node → Python Flow

```text id="r0b3nj"
Client
  │
  │ POST /api/sentiment/predict
  ▼
Node Controller
  │
  ▼
sentimentPythonService
  │
  │ POST /sentiment/predict-sentiment
  ▼
FastAPI :8002
  │
  ▼
DistilBERT
  │
  ▼
Prediction
  │
  ▼
Python → Node
```

This is the same microservice separation used by the Dropout and Recommendation modules.

---

# 13. Database Persistence

After Python returns the prediction, Node persists it into:

```text id="y6rvvi"
education.sentiment_predictions
```

The current table contains:

| Column           | Type             | Purpose                       |
| ---------------- | ---------------- | ----------------------------- |
| `id`             | UUID             | Prediction record ID          |
| `post_id`        | UUID             | Original post identifier      |
| `prediction`     | VARCHAR          | NEGATIVE / NEUTRAL / POSITIVE |
| `confidence`     | DOUBLE PRECISION | Highest class probability     |
| `negative_score` | DOUBLE PRECISION | Negative probability          |
| `neutral_score`  | DOUBLE PRECISION | Neutral probability           |
| `positive_score` | DOUBLE PRECISION | Positive probability          |
| `predicted_at`   | TIMESTAMP        | Prediction timestamp          |
| `model_version`  | VARCHAR          | Model version                 |

This follows the finalized AI schema. 

---

# 14. Database Ownership

The production responsibility is deliberately separated.

### Node.js

```text id="s72b8u"
✓ PostgreSQL connection
✓ Database queries
✓ Prediction persistence
✓ API orchestration
```

### Python

```text id="u6r8z2"
✓ Text preprocessing
✓ Tokenization
✓ DistilBERT inference
✓ Probability calculation
✓ Sentiment classification
```

Python contains **no production PostgreSQL connection**.

---

# 15. Example End-to-End Request

### Client request

```json id="f5xj20"
{
  "post_id": "21de70eb-efcd-47d0-99e3-72928628d228",
  "post_text": "This course is absolutely amazing and very useful."
}
```

### Node → Python

Same payload is forwarded to the Python service.

### Model result

```json id="x7n2ao"
{
  "post_id": "21de70eb-efcd-47d0-99e3-72928628d228",
  "prediction": "POSITIVE",
  "confidence": 97.03,
  "negative_score": 1.74,
  "neutral_score": 1.23,
  "positive_score": 97.03,
  "model_version": "1.0.0"
}
```

### Database record

A corresponding record is inserted into:

```text
education.sentiment_predictions
```

Your actual end-to-end test successfully created a PostgreSQL row with:

```text
prediction       POSITIVE
confidence       97.03
negative_score   1.74
neutral_score    1.23
positive_score   97.03
model_version    1.0.0
```

---

# 16. Model Versioning

The service reads:

```text id="4uj3gc"
MODEL_VERSION
```

from the environment.

Default:

```text
1.0.0
```

The version is persisted with every prediction.

This allows future predictions to be traced back to the model version that generated them.

Example:

```text id="9h7y6w"
Prediction A → model_version 1.0.0
Prediction B → model_version 1.1.0
```

This is important for production model monitoring and rollback.

---

# 17. Error Handling

The API handles:

### Invalid `post_id`

FastAPI/Pydantic rejects invalid UUID values.

### Missing `post_id`

Request validation fails.

### Missing text

Request validation fails.

### Text too short

The API requires at least two characters.

### Text too long

The API limits the request to 5000 characters.

### Python service unavailable

Node returns:

```text
503 Sentiment service unavailable.
```

### Python service timeout

Node returns:

```text
504 Sentiment service timed out.
```

---

# 18. Performance

The inference path is:

```text id="9xwz7k"
HTTP request
    ↓
Tokenization
    ↓
DistilBERT inference
    ↓
Softmax
    ↓
JSON response
```

There is no database query inside the Python inference path.

This minimizes coupling and allows the Python service to be independently scaled.

---

# 19. Production Deployment

Recommended deployment:

```text id="8d5s7j"
                 API Gateway
                      │
                      ▼
                 Node.js API
                    :3000
                      │
             ┌────────┴────────┐
             ▼                 ▼
        PostgreSQL        Python Service
                              :8002
                                │
                                ▼
                            DistilBERT
```

The Python service can be deployed independently from the Node backend.

---

# 20. Security

Production Python code should contain **no**:

```text id="gk0pna"
PostgreSQL password
Database URL
SQLAlchemy engine
PostgreSQL credentials
```

Sensitive configuration should remain in environment variables.

The Node `.env` must not be committed to Git.

---

# 21. Logging and Monitoring

Production monitoring should capture:

```text id="2xk8j7"
Request count
Prediction latency
Model inference latency
Prediction distribution
Confidence distribution
Model version
Python service errors
Node → Python failures
Database persistence failures
```

Useful monitoring metrics:

```text
POSITIVE %
NEUTRAL %
NEGATIVE %
Average confidence
Low-confidence prediction rate
Requests/minute
P95/P99 latency
```

---

# 22. Model Monitoring

Because sentiment distributions can change over time, monitor for:

```text id="4z4qz9"
Data drift
Language/style changes
Confidence degradation
Class imbalance
Prediction distribution changes
```

Model performance should periodically be evaluated against manually labeled production samples.

---

# 23. Testing Checklist

### Python

```text id="j0i6vl"
☑ Model loads
☑ Sentiment service loads
☑ FastAPI starts
☑ Health endpoint works
☑ Valid prediction works
☑ UUID validation works
☑ Text validation works
☑ Three sentiment classes work
```

### Node

```text id="w7r4t9"
☑ Python service connection works
☑ Controller works
☑ Route works
☑ Error handling works
☑ Python response received
☑ Database persistence works
```

### PostgreSQL

```text id="q6r3fc"
☑ education.sentiment_predictions exists
☑ UUID post_id supported
☑ Prediction stored
☑ Confidence stored
☑ All three scores stored
☑ Model version stored
☑ Timestamp stored
```

---

# 24. End-to-End Acceptance Test

The final tested architecture is:

```text id="f9yq1w"
POST
/api/sentiment/predict
        │
        ▼
Node.js
        │
        ▼
sentimentPythonService
        │
        ▼
FastAPI :8002
        │
        ▼
DistilBERT
        │
        ▼
POSITIVE / NEGATIVE / NEUTRAL
        │
        ▼
Node.js
        │
        ▼
education.sentiment_predictions
        │
        ▼
PostgreSQL
```

**Status: ✅ End-to-end tested successfully.**

---

# 25. Production Acceptance Criteria

```text id="2b3d8w"
✅ DistilBERT model loads successfully
✅ Python service has no DB dependency
✅ Standalone FastAPI service works
✅ Sentiment classification works
✅ Confidence calculated
✅ Negative/neutral/positive scores calculated
✅ Model version returned
✅ Node → Python communication works
✅ Node controller works
✅ Node route works
✅ PostgreSQL persistence works
✅ UUID post_id supported
✅ Database schema aligned with backend
✅ Legacy direct-DB Python runtime removed
✅ End-to-end pipeline tested
```

---



> **EduSaaS Sentiment Analysis is a DistilBERT-based NLP microservice that classifies learner discussion posts into Positive, Neutral, or Negative sentiment. The service tokenizes incoming discussion text, performs Transformer-based inference, calculates class probabilities, determines the highest-confidence sentiment, and returns the prediction with confidence, class scores, and model version. The Node.js backend acts as the orchestration and persistence layer, while Python is responsible exclusively for ML inference. Predictions are stored in the existing `education.sentiment_predictions` table using the post UUID, sentiment result, confidence, class probabilities, timestamp, and model version. The complete Node → FastAPI → DistilBERT → Node → PostgreSQL pipeline has been successfully tested.**

