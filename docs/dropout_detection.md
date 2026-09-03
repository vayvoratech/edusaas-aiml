The model produces:

* `dropout_prediction`
* `dropout_probability`
* `risk_level`

The current implementation uses a **Random Forest classifier**.

---

# 2. Production Architecture

```text
                    Frontend / Client
                           │
                           ▼
                    Node.js Backend
                         :3000
                           │
                           │ Fetch learner data
                           ▼
                    PostgreSQL
                  education schema
                           │
                           │
                           ▼
                Node Dropout Data Service
                           │
                           │ JSON
                           ▼
                 Python FastAPI Service
                         :8001
                           │
                           ▼
                 Dropout Prediction Model
                    Random Forest
                           │
                           ▼
                 Prediction + Probability
                           │
                           ▼
                    Python Response
                           │
                           ▼
                     Node.js
                           │
                           ▼
                Frontend / API Response
```

The key architectural principle is the same as Recommendation:

> **Node owns database access. Python owns ML inference.**

Python does not directly connect to PostgreSQL during prediction.

---

# 3. Model

### Algorithm

**Random Forest Classifier**

Random Forest is an ensemble learning algorithm consisting of multiple decision trees whose predictions are aggregated to produce the final classification.

For EduSaaS, it is used as a binary classifier:

```text
0 → No dropout
1 → Dropout
```

---

# 4. Input Features

The model uses learner engagement and performance features.

### Engagement Features

```text
sessions_last_30_days
avg_session_minutes
videos_watched
assignments_attempted
discussion_interactions
logins_last_30_days
days_since_last_login
```

### Learning/Progress Features

```text
completion_percentage
quiz_average
assignment_completion_rate
```

The Node `dropoutDataService` aggregates these values from the backend's education tables before sending them to Python.

---

# 5. Feature Definitions

| Feature                      | Description                                         |
| ---------------------------- | --------------------------------------------------- |
| `sessions_last_30_days`      | Number of learning sessions during the last 30 days |
| `avg_session_minutes`        | Average duration of learner sessions                |
| `videos_watched`             | Number of learning videos watched                   |
| `assignments_attempted`      | Number of assignments attempted                     |
| `discussion_interactions`    | Learner interactions with course discussions        |
| `logins_last_30_days`        | Number of learner logins during the last 30 days    |
| `days_since_last_login`      | Days since the learner's latest login               |
| `completion_percentage`      | Overall course completion percentage                |
| `quiz_average`               | Average quiz performance                            |
| `assignment_completion_rate` | Assignment completion ratio                         |

---

# 6. Data Flow

The Node backend collects learner information from the database.

Conceptually:

```text
education.activity_logs
        │
        ├── sessions_last_30_days
        ├── avg_session_minutes
        ├── videos_watched
        ├── assignments_attempted
        └── discussion_interactions

education.login_history
        │
        ├── logins_last_30_days
        └── days_since_last_login

education.progress
        │
        ├── quiz_score
        └── assignment_status

education.enrollments
        │
        └── completion_percentage
```

The Node service combines these into the model input.

This follows the finalized backend architecture where AI models consume backend-owned `education.*` tables rather than recreating legacy AI tables. 

---

# 7. Node → Python Contract

Node sends a JSON payload similar to:

```json
{
  "student_id": "2789a8b8-8ed0-496b-a38a-db56b91859ff",
  "sessions_last_30_days": 39,
  "avg_session_minutes": 82.2,
  "videos_watched": 75,
  "assignments_attempted": 17,
  "discussion_interactions": 30,
  "logins_last_30_days": 30,
  "days_since_last_login": 7,
  "completion_percentage": 46.38,
  "quiz_average": 69.95,
  "assignment_completion_rate": 0
}
```

Python receives this payload through FastAPI.

---

# 8. Python Inference Pipeline

```text
Request
   ↓
Pydantic validation
   ↓
Feature extraction
   ↓
Feature ordering
   ↓
Random Forest
   ↓
Class prediction
   ↓
Probability estimation
   ↓
Risk classification
   ↓
JSON response
```

The model uses the same feature ordering established during training.

This is important because ML models require the inference feature vector to match the training feature schema.

---

# 9. Prediction

The Random Forest generates a binary prediction:

```text
dropout_prediction = 0
```

or:

```text
dropout_prediction = 1
```

It also calculates the probability associated with the dropout class.

Example:

```text
dropout_probability = 0.35
```

This means the model estimates approximately:

```text
35% probability of dropout
```

for the supplied feature vector.

---

# 10. Risk Classification

The probability is converted into a human-readable risk level.

Current output categories:

```text
LOW
MEDIUM
HIGH
```

Example:

```json
{
  "dropout_prediction": 0,
  "dropout_probability": 0.35,
  "risk_level": "LOW"
}
```

Your tested production pipeline returned:

```text
Prediction: 0
Probability: 0.35
Risk: LOW
```

---

# 11. API Architecture

### Python API

```text
POST /dropout/predict
```

Python service:

```text
127.0.0.1:8001
```

The FastAPI application has been independently tested and successfully returned HTTP `200`.

### Node API

The frontend/application-facing endpoint is:

```text
POST /api/dropout/predict
```

Node receives the learner identifier, obtains the required data, calls Python, and returns the prediction.

---

# 12. Database Integration

The Dropout model does **not** directly query PostgreSQL.

Instead:

```text
PostgreSQL
     ↓
Node
     ↓
DropoutDataService
     ↓
Python API
     ↓
Random Forest
```

This provides clear separation of responsibilities.

### Node responsibility

```text
Database connection
SQL queries
Feature aggregation
Python API communication
API response
```

### Python responsibility

```text
Input validation
Feature preprocessing
Model inference
Probability calculation
Risk classification
```

---

# 13. Backend Tables

The current Dropout data pipeline uses backend-owned tables including:

### `education.activity_logs`

Provides:

```text
sessions_last_30_days
avg_session_minutes
videos_watched
assignments_attempted
discussion_interactions
```

### `education.login_history`

Provides:

```text
logins_last_30_days
days_since_last_login
```

### `education.progress`

Provides:

```text
quiz_score
assignment_status
```

### `education.enrollments`

Provides:

```text
completion_percentage
```

The backend schema documentation establishes `education.enrollments`, `education.progress`, and the activity/login structures as backend-owned data sources for AI features. 

---

# 14. Tested Data Retrieval

The Node service was successfully tested independently.

For example, a learner request returned:

```json
{
  "student_id": "2789a8b8-8ed0-496b-a38a-db56b91859ff",
  "sessions_last_30_days": 39,
  "avg_session_minutes": 82.2,
  "videos_watched": 75,
  "assignments_attempted": 17,
  "discussion_interactions": 30,
  "logins_last_30_days": 30,
  "days_since_last_login": 7,
  "completion_percentage": 46.38,
  "quiz_average": 69.95,
  "assignment_completion_rate": 0
}
```

This confirms that Node successfully converts backend data into the ML feature payload.

---

# 15. Tested Model Response

The Python model successfully returned:

```json
{
  "success": true,
  "message": "Dropout prediction completed successfully.",
  "data": {
    "student_id": "2789a8b8-8ed0-496b-a38a-db56b91859ff",
    "dropout_prediction": 0,
    "dropout_probability": 0.35,
    "risk_level": "LOW"
  }
}
```

---

# 16. End-to-End Pipeline

The complete tested pipeline is:

```text
Frontend
   │
   ▼
POST /api/dropout/predict
   │
   ▼
Node.js
   │
   ├── Get student ID
   │
   ├── Query education schema
   │
   └── Build ML feature payload
   │
   ▼
POST /dropout/predict
   │
   ▼
FastAPI :8001
   │
   ▼
Random Forest
   │
   ├── Prediction
   └── Probability
   │
   ▼
Risk Classification
   │
   ▼
Python → Node
   │
   ▼
Node → Client
```

---

# 17. Error Handling

The production implementation should handle:

### Student not found

```text
404 / appropriate application error
```

### Missing dropout data

```text
No dropout data found for this student.
```

This condition was explicitly encountered during testing when a student UUID had no corresponding activity/login/progress data.

### Python service unavailable

Node should return a service-unavailable response rather than silently generating a prediction.

### Invalid feature values

FastAPI/Pydantic validation should reject malformed payloads.

---

# 18. Model Artifacts

The Random Forest model and its feature-column metadata are maintained as model artifacts.

Conceptually:

```text
models/
├── dropout_random_forest.pkl
└── dropout_feature_columns.pkl
```

The feature-column artifact is important because it ensures inference uses the same feature ordering as training.

---

# 19. Model Evaluation

The model was previously evaluated using a train/test split.

Recorded evaluation:

```text
Dataset:
1000 records

Training:
800

Testing:
200
```

Metrics:

```text
Accuracy:       0.86
ROC-AUC:        0.9119
Dropout Recall: 82%
```

Confusion matrix:

```text
[[119, 16],
 [ 12, 53]]
```

These metrics indicate that the model has useful discriminative performance, with particular attention to dropout recall.

For production monitoring, these metrics should be periodically recalculated against newly labeled learner outcomes.

---

# 20. Monitoring Requirements

Production monitoring should track:

```text
Prediction volume
Dropout probability distribution
LOW/MEDIUM/HIGH distribution
Prediction latency
Python service errors
Node → Python failures
Missing learner data
Feature drift
Model performance
```

Most importantly, monitor **false negatives**, because incorrectly classifying a genuinely at-risk learner as LOW risk can prevent timely intervention.

---

# 21. Security

The Python service must not contain:

```text
PostgreSQL password
DB_URL
Direct SQL queries
Production database credentials
```

The Node backend owns database credentials.

Sensitive values belong in environment variables and should never be committed to Git.

---

# 22. Production Deployment

Recommended deployment:

```text
                 API Gateway / Load Balancer
                           │
                           ▼
                      Node.js API
                         :3000
                           │
              ┌────────────┴─────────────┐
              ▼                          ▼
         PostgreSQL              Python ML Service
                                      :8001
                                        │
                                        ▼
                                Random Forest Model
```

The Python service can be independently scaled if prediction volume increases.

---

# 23. Performance Considerations

The inference path should remain lightweight:

```text
Node DB aggregation
        ↓
Small JSON payload
        ↓
Random Forest inference
        ↓
Immediate response
```

Avoid putting database operations inside the Python prediction request.

For higher production traffic, Node can use connection pooling and the Python service can run multiple worker processes/containers.

---

# 24. Production Acceptance Criteria

```text
✅ Random Forest model loaded successfully
✅ Feature schema validated
✅ Python API runs independently
✅ Python has no DB dependency
✅ Node retrieves learner data
✅ Node builds feature payload
✅ Node → Python communication works
✅ Dropout prediction generated
✅ Dropout probability generated
✅ Risk level generated
✅ Node API works
✅ End-to-end pipeline tested
✅ PostgreSQL remains owned by Node
✅ Secrets excluded from Git
```

---
